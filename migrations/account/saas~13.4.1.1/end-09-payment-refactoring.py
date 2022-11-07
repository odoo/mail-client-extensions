# -*- coding: utf-8 -*-
import json
import logging
from datetime import date, timedelta

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.accounting import no_deprecated_accounts, no_fiscal_lock

_logger = logging.getLogger("odoo.upgrade.account.saas-13.4." + __name__)

MOVE_BATCH = 48


def search_new_account_code(cr, company_id, digits, prefix):
    cr.execute(
        """
            WITH codes AS (
               SELECT left(%s || repeat('0', %s), %s-1) || generate_series as code
                 FROM generate_series(1,10000))
            SELECT c.code
              FROM codes c
             WHERE NOT EXISTS (SELECT 1 FROM account_account a WHERE a.code = c.code AND a.company_id = %s)
             LIMIT 1
        """,
        [prefix, digits, digits, company_id],
    )
    return cr.fetchone()[0] if cr.rowcount else False


def migrate(cr, version):

    util.recompute_fields(cr, "account.bank.statement.line", ["amount_residual", "is_reconciled"])

    env = util.env(cr)

    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    # ===== FIX CONFIG =====

    # Set the fiscalyear lock date in case it was empty, in order to ensure the integrity of the accounting as much as possible
    lock_date = date.today() - timedelta(weeks=26)
    # If the lock date is more than 1.5 years old, reset it to a more recent date.
    limit_date = date.today() - timedelta(weeks=78)
    missing_lockdate_companies = env["res.company"].search(
        ["|", ("fiscalyear_lock_date", "=", False), ("fiscalyear_lock_date", "<", limit_date)]
    )
    if missing_lockdate_companies:
        missing_lockdate_companies._write({"fiscalyear_lock_date": lock_date})
        companies = ", ".join(missing_lockdate_companies.mapped("name"))
        msg = (
            "Following a refactoring in how the payments (bank statements) work in the accounting of Odoo 14.0, "
            "the lock date, defining a date limit before which the accounts must be left untouched, "
            "has to be set on your companies for the upgrade. "
            "Without it, the upgrade could change your accounting for periods you consider as closed/locked. "
            f"As the lock date was not set on your company(ies) {companies} (or they were very old), "
            f"it has been set automatically to {lock_date}. "
            "If you do not agree with this lock date, please set your lock date on your company(ies) before upgrading "
            "your database."
        )
        util.add_to_migration_reports(msg, "Accounting")

    # Fix default suspense account for res.company that is the account used as counterpart on draft bank statement lines.
    _create_journal = env["account.chart.template"]._create_liquidity_journal_suspense_account
    for company in env["res.company"].search([]):
        code_digits = company.chart_template_id.code_digits or 6
        company.account_journal_suspense_account_id = _create_journal(company, code_digits)

    # Fix additional 'payment_debit_account_id', 'payment_credit_account_id', 'suspense_account_id' on account.journal.
    # payment_debit_account_id/payment_credit_account_id are the new accounts used by the account.payments instead of
    # default_debit_account_id/default_credit_account_id.
    # suspense_account_id is the same as the one set on the company but allowing to have a custom one by journal.
    cr.execute(
        """
        SELECT id
          FROM account_journal
         WHERE type IN ('bank', 'cash')
            OR id IN (
                 SELECT journal_id from account_bank_statement_line_pre_backup
                  UNION
                 SELECT journal_id from account_payment_pre_backup
           )
        """
    )
    journal_ids = [journal_id for journal_id, in cr.fetchall()]
    current_assets_type = env.ref("account.data_account_type_current_assets")
    liquidity_type = env.ref("account.data_account_type_liquidity")
    for journal in util.iter_browse(env["account.journal"], journal_ids):
        digits = journal.company_id.chart_template_id.code_digits or 6

        if journal.type == "bank":
            liquidity_account_prefix = journal.company_id.bank_account_code_prefix or ""
        else:
            liquidity_account_prefix = (
                journal.company_id.cash_account_code_prefix or journal.company_id.bank_account_code_prefix or ""
            )

        default_account_id = journal.default_account_id
        if not default_account_id:
            liquidity_account = {
                "name": journal.name,
                "code": search_new_account_code(cr, journal.company_id.id, digits, liquidity_account_prefix),
                "user_type_id": liquidity_type.id,
                "company_id": journal.company_id.id,
                "currency_id": journal.currency_id.id if journal.currency_id else journal.company_id.currency_id.id,
            }
            default_account_id = env["account.account"].create(liquidity_account)

        if default_account_id.user_type_id == liquidity_type:
            debit_account = {
                "name": "Outstanding Receipts",
                "code": search_new_account_code(cr, journal.company_id.id, digits, liquidity_account_prefix),
                "reconcile": True,
                "user_type_id": current_assets_type.id,
                "company_id": journal.company_id.id,
            }
            j1 = env["account.account"].create(debit_account)

            credit_account = {
                "name": "Outstanding Payments",
                "code": search_new_account_code(cr, journal.company_id.id, digits, liquidity_account_prefix),
                "reconcile": True,
                "user_type_id": current_assets_type.id,
                "company_id": journal.company_id.id,
            }
            j2 = env["account.account"].create(credit_account)
        else:
            j1 = default_account_id
            j2 = default_account_id

        cr.execute(
            """
                UPDATE account_journal
                   SET payment_debit_account_id=%s,
                       payment_credit_account_id=%s,
                       suspense_account_id=%s,
                       default_account_id=%s
                 WHERE id=%s
            """,
            [
                j1.id,
                j2.id,
                journal.company_id.account_journal_suspense_account_id.id,
                default_account_id.id,
                journal.id,
            ],
        )

        cr.execute("SELECT 1 FROM journal_account_control_rel WHERE journal_id=%s", [journal.id])
        if cr.fetchall():
            cr.execute(
                """
                    INSERT INTO journal_account_control_rel (journal_id, account_id)
                    VALUES (%(journal)s, %(debit)s), (%(journal)s, %(credit)s), (%(journal)s, %(suspense)s)
                    ON CONFLICT DO NOTHING
                """,
                {
                    "journal": journal.id,
                    "debit": j1.id,
                    "credit": j2.id,
                    "suspense": journal.company_id.account_journal_suspense_account_id.id,
                },
            )

    # ===== FIX res.partner's company =====
    # Some partners can have a company != move company...

    cr.execute(
        """
        CREATE TABLE wrong_company_partners AS (
            SELECT
                res_partner.id AS partner_id,
                res_partner.company_id AS company_id
            FROM res_partner
            JOIN account_bank_statement_line_pre_backup st_line_backup ON st_line_backup.partner_id = res_partner.id
            JOIN account_journal journal ON journal.id = st_line_backup.journal_id
            WHERE res_partner.company_id IS NOT NULL
            AND res_partner.company_id != journal.company_id

            UNION

            SELECT res_partner.id, res_partner.company_id
            FROM res_partner
            JOIN account_payment_pre_backup pay_backup ON pay_backup.partner_id = res_partner.id
            JOIN account_journal journal ON journal.id = pay_backup.journal_id
            WHERE res_partner.company_id IS NOT NULL
            AND res_partner.company_id != journal.company_id
        )
    """
    )
    cr.execute(
        """
            UPDATE res_partner
               SET company_id = NULL
              FROM wrong_company_partners mapping
             WHERE mapping.partner_id = res_partner.id
        """
    )

    # ===== FIX deprecated account.account =====

    cr.execute("UPDATE account_account SET deprecated = false WHERE deprecated = true RETURNING id")
    deprecated_account_ids = [res[0] for res in cr.fetchall()]

    # ===== FIX res.partner.bank's company =====
    # Some res.partner.bank can have a company != move company...

    cr.execute(
        """
        SELECT res_partner_bank.id, res_partner_bank.company_id
        FROM account_payment_pre_backup pay_backup
        JOIN res_partner_bank ON res_partner_bank.id = pay_backup.partner_bank_account_id
        WHERE res_partner_bank.company_id IS NOT NULL

        UNION

        SELECT res_partner_bank.id, res_partner_bank.company_id
        FROM account_bank_statement_line_pre_backup st_line_backup
        JOIN res_partner_bank ON res_partner_bank.id = st_line_backup.bank_account_id
        WHERE res_partner_bank.company_id IS NOT NULL

        UNION

        SELECT res_partner_bank.id, res_partner_bank.company_id
        FROM account_journal journal
        JOIN res_partner_bank ON res_partner_bank.id = journal.bank_account_id
        WHERE res_partner_bank.company_id IS NOT NULL
        """
    )
    wrong_company_partner_bank_ids = dict(cr.fetchall())
    if wrong_company_partner_bank_ids:
        cr.execute(
            "UPDATE res_partner_bank SET company_id = NULL WHERE id in %s",
            [tuple(wrong_company_partner_bank_ids.keys())],
        )

    # ===== Posted account.payment =====

    # Manually deleted journal entries for posted payments.

    cr.execute(
        """
        SELECT pay.id
        FROM account_payment pay
        JOIN account_payment_pre_backup pay_backup ON pay_backup.id = pay.id
        WHERE pay_backup.state NOT IN ('draft', 'cancelled')
        AND pay.move_id IS NULL
    """
    )
    payment_ids = [res[0] for res in cr.fetchall()]
    if payment_ids:
        util.add_to_migration_reports(
            "The following payments have been deleted during the migration because there were posted but no longer"
            "linked to any journal entry: %s" % payment_ids,
            "Accounting",
        )
        _logger.info("Removing %s posted payments that are not linked to any journal entry.", len(payment_ids))
        util.iter_browse(env["account.payment"], payment_ids, strategy="commit").unlink()

    # Change the liquidity account of payments that are not yet reconciled with a statement line.
    # This should be done because the payment is no longer impacting directly the bank/cash account like the
    # statement line does. Instead, we use a temporary liquidity account.
    # To work retroactively, this must be done only on journal entry that are not shared between
    # an account.bank.statement.line and an account.payment.
    # This part is done in 'post' because new account.account are created in 'post' to migrate
    # the account.journal.
    # //execute (thanks to line balce split)
    # avoid to set a null value: new row for relation "account_move_line" violates check
    # constraint "account_move_line_check_accountable_required_fields"

    if util.version_gte("saas~13.5"):
        account_cmp = " = journal.default_account_id"
    else:
        account_cmp = "IN (journal.default_debit_account_id, journal.default_credit_account_id)"

    ctx = {"skip_account_move_synchronization": True, "tracking_disable": True}
    move_ids = set()
    for debit_credit, balance_sign in (("debit", ">="), ("credit", "<")):
        cr.execute(
            f"""
            UPDATE account_move_line line
            SET account_id = journal.payment_{debit_credit}_account_id
            FROM account_payment pay
            JOIN account_payment_pre_backup pay_backup ON pay_backup.id = pay.id
            JOIN account_move move ON move.id = pay.move_id
            JOIN res_company company ON move.company_id = company.id
            JOIN account_journal journal ON journal.id = move.journal_id
            WHERE pay_backup.no_replace_account IS FALSE
            AND move.statement_line_id IS NULL
            AND line.move_id = move.id
            AND line.account_id {account_cmp}
            AND line.balance {balance_sign} 0.0
            AND journal.payment_{debit_credit}_account_id IS NOT NULL
            AND NOT EXISTS(SELECT 1 FROM account_partial_reconcile part WHERE part.{debit_credit}_move_id = line.id)
            AND (company.fiscalyear_lock_date IS NULL OR line.date > company.fiscalyear_lock_date)
            RETURNING move.id
        """
        )
        updated_move_ids = set(r[0] for r in cr.fetchall())
        move_ids |= updated_move_ids
        if updated_move_ids:
            other = "credit" if debit_credit == "debit" else "debit"
            cr.execute(
                f"""
                SELECT {debit_credit}_move.id
                FROM account_partial_reconcile reconcile
                JOIN account_move_line debit_line ON debit_line.id = reconcile.debit_move_id
                JOIN account_move_line credit_line ON credit_line.id = reconcile.credit_move_id
                JOIN account_move debit_move ON debit_move.id = debit_line.move_id
                JOIN account_move credit_move ON credit_move.id = credit_line.move_id
                WHERE {other}_move.id IN %(move_ids)s
            """,
                {"move_ids": tuple(updated_move_ids)},
            )
            move_ids |= set(r[0] for r in cr.fetchall())
    if move_ids:
        cr.execute("SELECT payment_id FROM account_move WHERE id IN %s AND payment_id IS NOT NULL", [tuple(move_ids)])
        payment_ids = set(r[0] for r in cr.fetchall())
        util.recompute_fields(
            cr,
            env["account.payment"].with_context(**ctx),
            fields=("is_reconciled",),
            ids=payment_ids,
            chunk_size=1024,
        )
        util.recompute_fields(
            cr,
            env["account.move"].with_context(**ctx),
            fields=("payment_state",),
            ids=move_ids,
            chunk_size=1024,
        )

    with no_fiscal_lock(cr):

        # ===== Draft/cancelled account.payment =====
        env["account.payment"].flush()
        created_move_ids = set()
        chunk_size = 48
        ncr = util.named_cursor(cr)
        ncr.execute(
            """
            SELECT
                pay_backup.journal_id,
                pay_backup.id AS payment_id,
                pay_backup.payment_date AS date,
                pay_backup.partner_id,
                '/' as name,
                pay_backup.currency_id
            FROM account_payment_pre_backup pay_backup
            JOIN account_payment pay ON pay.id = pay_backup.id
            WHERE pay_backup.state IN ('draft', 'cancelled')
            AND pay.move_id IS NULL
            """
        )
        for data in util.log_chunks(
            ncr.iterdict(), _logger, chunk_size=chunk_size, qualifier=f"account.move {chunk_size}-bucket"
        ):
            moves = env["account.move"].with_context(**ctx).create(data)

            query = """
                UPDATE account_payment
                   SET move_id = ('{}'::jsonb->>id::varchar)::int4
                 WHERE id IN %s
            """
            mapping = {move.payment_id.id: move.id for move in moves}
            cr.execute(query.format(json.dumps(mapping)), [tuple(mapping)])

            moves.invalidate_cache()
            moves.payment_id._compute_destination_account_id()
            invalid_moves = moves.filtered(lambda m: not m.payment_id.destination_account_id)
            if invalid_moves:
                util.add_to_migration_reports(
                    """
                        <details>
                        <summary>
                            The following payments have been deleted because the accounting was not correctly configured
                            and it wasn't possible to determine a destination account for them.
                        </summary>
                        <ul>%s</ul>
                        </details>
                    """
                    % (
                        "\n".join(
                            "<li>%s(#%s)</li>" % (util.html_escape(move.payment_id.name), move.payment_id.id)
                            for move in invalid_moves
                        ),
                    ),
                    "Accounting",
                    format="html",
                )
                moves -= invalid_moves
                for invalid in invalid_moves:
                    mapping.pop(invalid.payment_id.id)
                invalid_moves.unlink()

            move_lines_to_create = []
            for move in moves:
                created_move_ids.add(move.id)
                for vals in move.payment_id._prepare_move_line_default_vals():
                    move_lines_to_create.append({**vals, "move_id": move.id, "exclude_from_invoice_tab": True})

            env["account.move.line"].with_context(**ctx).create(move_lines_to_create)

            # Newly created moves for cancelled payments must be cancelled as well.
            cr.execute(
                """
                SELECT pay_backup.id
                  FROM account_payment_pre_backup pay_backup
                  JOIN account_move m ON pay_backup.id = m.payment_id
                 WHERE pay_backup.state = 'cancelled'
                   AND m.id = ANY(%s)
                """,
                [list(moves.ids)],
            )
            cancelled_payment_ids = [res[0] for res in cr.fetchall()]
            if cancelled_payment_ids:
                env["account.payment"].browse(cancelled_payment_ids).with_context(**ctx).action_cancel()

            env["base"].with_context(**ctx).flush()
            env.cr.commit()

        ncr.close()
        # ===== Synchronize account.payment <=> account.move =====

        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                """
                UPDATE account_move
                   SET payment_id = account_payment.id
                  FROM account_payment
                 WHERE account_payment.move_id = account_move.id
                   AND account_move.payment_id IS NULL
                """,
                table="account_move",
            ),
        )

        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                """
                UPDATE account_move_line
                   SET payment_id = move.payment_id
                  FROM account_move move
                 WHERE account_move_line.move_id = move.id
                """,
                table="account_move_line",
            ),
        )

        # ===== Draft account.bank.statement.line =====

        # Create account.move for 'draft' statement line.
        cr.execute(
            """
            SELECT
                st_line_backup.ref,
                st_line_backup.date,
                st_line_backup.note AS narration,
                st_line_backup.id AS statement_line_id,
                st_line_backup.journal_id,
                st_line_backup.partner_id,
                '/' as name,
                COALESCE(journal.currency_id, company.currency_id) AS currency_id
            FROM account_bank_statement_line_pre_backup st_line_backup
            JOIN account_bank_statement_line st_line ON st_line.id = st_line_backup.id
            JOIN account_journal journal ON journal.id = st_line.journal_id
            JOIN res_company company ON company.id = journal.company_id
            WHERE st_line.move_id IS NULL
            """
        )

        _logger.info("Creating %d moves for draft statement lines", cr.rowcount)

        for data in util.chunks(cr.dictfetchall(), size=48, fmt=list):
            moves = env["account.move"].with_context(**ctx).create(data)

            query = """
                UPDATE account_bank_statement_line
                   SET move_id = ('{}'::jsonb->>id::varchar)::int4
                 WHERE id IN %s
            """
            mapping = {move.statement_line_id.id: move.id for move in moves}
            cr.execute(query.format(json.dumps(mapping)), [tuple(mapping)])

            cr.execute(
                """
                UPDATE account_move move
                SET currency_id = COALESCE(journal.currency_id, company.currency_id),
                    partner_id = st_line_backup.partner_id,
                    partner_bank_id = st_line_backup.bank_account_id,
                    journal_id = st_line_backup.journal_id,
                    narration = st_line_backup.note,
                    company_id = st_line_backup.company_id
                FROM account_bank_statement_line_pre_backup st_line_backup
                JOIN account_bank_statement_line st_line ON st_line.id = st_line_backup.id
                JOIN account_journal journal ON journal.id = st_line_backup.journal_id
                JOIN res_company company ON company.id = journal.company_id
                WHERE move.id = st_line.move_id
                AND move.id IN %s
                """,
                [tuple(moves.ids)],
            )

            moves.invalidate_cache()
            moves.statement_line_id.journal_id._compute_suspense_account_id()

            # for journals without type 'cash' or 'bank' that are still being used here
            for j in moves.statement_line_id.journal_id:
                if not j.suspense_account_id:
                    j.suspense_account_id = j.company_id.account_journal_suspense_account_id

            move_lines_to_create = []
            for move in moves:
                created_move_ids.add(move.id)
                for vals in move.statement_line_id._prepare_move_line_default_vals():
                    move_lines_to_create.append({**vals, "move_id": move.id, "exclude_from_invoice_tab": True})

            env["account.move.line"].with_context(**ctx).create(move_lines_to_create)

            env["account.move.line"].flush()

        # ===== Synchronize account.bank.statement.line <=> account.move =====

        _logger.info("Synchronize statement lines & moves")
        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                """
                UPDATE account_move
                   SET statement_line_id = account_bank_statement_line.id
                  FROM account_bank_statement_line
                 WHERE account_bank_statement_line.move_id = account_move.id
                   AND account_move.statement_line_id IS NULL
                """,
                table="account_move",
            ),
        )

        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                """
                UPDATE account_move_line
                   SET statement_line_id = move.statement_line_id,
                       statement_id = st_line.statement_id
                  FROM account_move move
                  JOIN account_bank_statement_line st_line ON st_line.id = move.statement_line_id
                 WHERE account_move_line.move_id = move.id
                """,
                table="account_move_line",
            ),
        )

        # ===== RESTORE res.partner's company =====

        _logger.info("restore deprecated accounts and company on partners and partner banks")
        cr.execute(
            """
            UPDATE res_partner
            SET company_id = mapping.company_id
            FROM wrong_company_partners mapping
            WHERE mapping.partner_id = res_partner.id
            """
        )
        cr.execute("DROP TABLE wrong_company_partners")

        # ===== RESTORE deprecated account.account =====

        if deprecated_account_ids:
            cr.execute("UPDATE account_account SET deprecated = TRUE WHERE id IN %s", [tuple(deprecated_account_ids)])

        # ===== RESTORE res.partner.bank's company =====
        if wrong_company_partner_bank_ids:
            query = """
                UPDATE res_partner_bank
                   SET company_id = ('{}'::jsonb->>id::varchar)::int4
                 WHERE id IN %s
            """
            cr.execute(
                query.format(json.dumps(wrong_company_partner_bank_ids)), [tuple(wrong_company_partner_bank_ids)]
            )

        # ===== MISC =====
        ctx = {"tracking_disable": True, "skip_account_move_synchronization": True}

        _logger.info("Post all bank statements that seem to be already processed")
        # Post all bank statements that seem to be already processed meaning the balance_end & balance_end_real must be
        # the same and not be part of a broken statement chain.

        domain = [("is_valid_balance_start", "=", True), ("difference", "=", 0.0), ("state", "=", "open")]
        bs_ids = env["account.bank.statement"].search(domain).ids
        with no_deprecated_accounts(cr):
            for bs in util.iter_browse(env["account.bank.statement"].with_context(**ctx), bs_ids):
                bs.button_post()

        _logger.info("Post newly created journal entries still in draft")
        # Since the 'post_at' field is gone, post the journal entries still in draft.
        cr.execute(
            """
            -- All reconciled entries must be posted
            SELECT move.id
            FROM account_partial_reconcile part
            JOIN account_move_line line ON
                line.id = part.debit_move_id
                OR
                line.id = part.credit_move_id
            JOIN account_move move ON move.id = line.move_id
            WHERE move.state = 'draft'
            AND not auto_post

            UNION

            -- Posted payments having a draft entry due to the post_at = 'bank_rec' on journal.
            SELECT pay.move_id
            FROM account_payment pay
            JOIN account_move move ON move.id = pay.move_id
            JOIN account_payment_pre_backup pay_backup ON pay_backup.id = pay.id
            JOIN account_journal_backup journal_backup ON journal_backup.id = pay_backup.journal_id
            WHERE journal_backup.post_at = 'bank_rec'
            AND pay_backup.state = 'posted'
            AND move.state = 'draft'
            AND move.statement_line_id IS NULL
            """
        )

        ids = [row[0] for row in cr.fetchall()]
        with no_deprecated_accounts(cr):
            util.iter_browse(env["account.move"].with_context(**ctx), ids, chunk_size=1024).action_post()

        if ids:
            cr.execute("SELECT move.id, move.name FROM account_move move WHERE move.id in %s", [tuple(ids)])
            posted_moves = [(row[0], row[1]) for row in cr.fetchall()]
            move_links = "".join(
                "<li>{}</li>".format(util.get_anchor_link_to_record("account.move", move_id, move_name))
                for move_id, move_name in posted_moves
            )
            msg = (
                "<details>"
                "<summary>"
                "Reconciling with journal items from journal entries in a draft state is no longer allowed. To ensure your "
                "database remains consistent, the following journal entries have been posted. If you wish to prevent this from "
                "happening, you will need to either ensure the affected entries are posted before the upgrade, or unreconcile "
                "their journal items."
                "</summary>"
                f"<ul>{move_links}</ul>"
                "</details>"
            )
            util.add_to_migration_reports(msg, "Accounting", format="html")

    # ===== Don't alter accounting data prior to the lock date =====

    if created_move_ids:
        cr.execute(
            """
            UPDATE account_move_line line
            SET parent_state = 'cancel'
            FROM res_company company
            WHERE company.id = line.company_id
            AND company.fiscalyear_lock_date IS NOT NULL
            AND line.date <= company.fiscalyear_lock_date
            AND line.move_id IN %s
        """,
            [tuple(created_move_ids)],
        )
        cr.execute(
            """
            UPDATE account_move
            SET auto_post = FALSE,
                state = 'cancel'
            FROM res_company company
            WHERE company.id = account_move.company_id
            AND company.fiscalyear_lock_date IS NOT NULL
            AND account_move.date <= company.fiscalyear_lock_date
            AND account_move.id IN %s
        """,
            [tuple(created_move_ids)],
        )

    # ==== CHECK move_id that must be set on all account.payment/account.bank.statement.line ====
    cr.execute("SELECT id FROM account_payment WHERE move_id IS NULL")
    for (payment_id,) in cr.fetchall():
        _logger.error("Missing move_id on account.payment (id=%s)", payment_id)

    cr.execute("SELECT id FROM account_bank_statement_line WHERE move_id IS NULL")
    for (st_line_id,) in cr.fetchall():
        _logger.error("Missing move_id on account.bank.statement.line (id=%s)", st_line_id)
