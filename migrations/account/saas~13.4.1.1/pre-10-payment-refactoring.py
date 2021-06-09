# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-13.4.1.1." + __name__)


def migrate(cr, version):

    msg = """
        <p><strong>IMPORTANT NOTICE</strong></p>
        <p>
            Payments have been heavily refactored in Odoo 14.0.
            To make sure the upgrade of your payments is done correctly,
            you should ensure a few things.
        </p>
        <p>
            Before upgrading:
            <ul>
                <li>
                    Check that the lock dates for all companies are correctly set;
                    the more recent the lock date, the better.
                </li>
                <li>
                    Check if the default accounts on the bank/cash journal is of type liquidity (bank/cash):
                <ul>
                    <li>In case they are, new outstanding payment accounts will be created during the migration.</li>
                    <li>In case they are current asset accounts, no new account will be created.</li>
                </ul>
                </li>
                <li>
                    Make sure all accounting entries have a consistant number regarding the fiscal year they belong to.
                    (e.g. a journal entry dated of 2019 shouldn’t have a name xx/2020/xx/xxxx)
                </li>
            </ul>
        </p>
        <p>
            After upgrading:
            <ul>
                <li>
                    Check the outstanding payment accounts are correctly created.
                    You will have to change the code/name to fit your own chart of accounts.
                </li>
            </ul>
        <ul>
            <li>
                Check that pre-recorded payments
                (recorded before migration, using the "register payment" button on invoices)
                in the not-locked periods can correctly be reconciled (after migration) with an incoming statement.
            </li>
        </ul>
        </p>
        <p>
            We highly encourage you to watch <a href="https://youtu.be/ZOxsB7F6omY" target="_blank">this video</a>
            explaining the differences between Odoo 13.0 and Odoo 14.0 when registering payments. You will need to decide
            which workflow you want to use. By default the upgrade will assume that your workflow is to reconcile all
            payments on invoices with bank transactions. Invoices will be marked "in payment" when a payment is registered
            and will only be marked as "paid" after reconciling with a bank transaction. If reconciling bank transactions
            is not part of your workflow, you should change the outstanding account for incoming and / or outgoing payments
            on the relevant bank journal to the bank account of that journal. If this is done, payments registered on
            invoices result in them being marked as "paid" right away, and it will no longer be possible to reconcile a bank
            transaction with them.
        </p>
    """
    util.add_to_migration_reports(msg, "Accounting", format="html")
    cr.execute(
        """
        UPDATE account_bank_statement_line st_line
           SET move_name = NULL
         WHERE move_name IN (SELECT name FROM account_move)
    """
    )

    cr.execute(
        """
        UPDATE account_bank_statement_line st_line
           SET move_name = NULL
          FROM account_bank_statement_line older_st_line
         WHERE st_line.move_name = older_st_line.move_name
           AND st_line.id > older_st_line.id
    """
    )

    # The currency_id and journal_currency_id shouldn't be same.
    cr.execute(
        """
           UPDATE account_bank_statement_line st_line
              SET amount_currency = 0.0,
                  currency_id = NULL
             FROM account_journal journal
             JOIN res_company com ON com.id = journal.company_id
            WHERE st_line.journal_id = journal.id
              AND (
                    st_line.currency_id IS NULL
                    OR
                    (COALESCE(amount_currency, 0.0) = 0.0)
                    OR
                    st_line.currency_id = COALESCE(journal.currency_id, com.currency_id)
                  )
        """
    )

    # ===========================================================
    # Invoice Analysis (PR:47066)
    # ===========================================================
    util.rename_field(cr, "account.invoice.report", "currency_id", "company_currency_id")
    for field in [
        "name",
        "invoice_payment_term_id",
        "invoice_partner_bank_id",
        "nbr_lines",
        "residual",
        "amount_total",
    ]:
        util.remove_field(cr, "account.invoice.report", field)

    # ===========================================================
    # Payment-pocalypse (PR: 41301 & 7019)
    # ===========================================================

    # Backup tables to use the old relational structure in post-* scripts.
    cr.execute("CREATE TABLE account_payment_pre_backup AS TABLE account_payment")
    cr.execute("CREATE TABLE account_bank_statement_line_pre_backup AS TABLE account_bank_statement_line")
    cr.execute("CREATE TABLE account_journal_backup AS (SELECT id, post_at FROM account_journal)")
    util.create_column(cr, "account_payment_pre_backup", "no_replace_account", "boolean", default=False)

    # Migrate columns / fields.

    # === Transients ===

    util.remove_model(cr, "account.bank.statement.import.journal.creation")

    util.remove_field(cr, "res.config.settings", "account_bank_reconciliation_start")

    for field_name in ("available_payment_methods", "invoice_company_id", "invoice_ids"):
        util.remove_field(cr, "account.payment.register", field_name)

    # === Reports ===

    util.rename_field(cr, "account.invoice.report", "type", "move_type")
    util.rename_field(cr, "account.invoice.report", "invoice_partner_bank_id", "partner_bank_id")

    # === Models ===

    util.create_column(cr, "account_move", "payment_id", "int4")
    util.create_column(cr, "account_move", "statement_line_id", "int4")
    util.rename_field(cr, "account.move", "type", "move_type")
    util.rename_field(cr, "account.move", "invoice_sent", "is_move_sent")
    util.rename_field(cr, "account.move", "invoice_partner_bank_id", "partner_bank_id")
    util.rename_field(cr, "account.move", "invoice_payment_ref", "payment_reference")

    util.rename_field(cr, "account.move.line", "tag_ids", "tax_tag_ids")

    util.create_column(cr, "account_chart_template", "account_journal_suspense_account_id", "int4")

    util.create_column(cr, "res_company", "account_journal_suspense_account_id", "int4")
    util.remove_field(cr, "res.company", "account_bank_reconciliation_start")

    util.create_column(cr, "account_journal", "payment_debit_account_id", "int4")
    util.create_column(cr, "account_journal", "payment_credit_account_id", "int4")
    util.create_column(cr, "account_journal", "suspense_account_id", "int4")
    util.remove_field(cr, "account.journal", "post_at")

    # ensure used bank/cash journals have default credit/debit account set
    cr.execute(
        """
            UPDATE account_journal
               SET default_debit_account_id = COALESCE(default_debit_account_id, default_credit_account_id),
                   default_credit_account_id = COALESCE(default_debit_account_id, default_credit_account_id)
             WHERE type IN ('bank', 'cash')
               AND NOT ( -- not both set
                    default_credit_account_id IS NOT NULL
                AND default_debit_account_id IS NOT NULL
               )
        """
    )

    util.create_column(cr, "account_bank_statement", "is_valid_balance_start", "boolean")
    util.remove_field(cr, "account.bank.statement", "accounting_date")

    util.create_column(cr, "account_bank_statement_line", "move_id", "int4")
    cr.execute("CREATE index ON account_bank_statement_line(move_id)")
    util.create_column(cr, "account_bank_statement_line", "amount_residual", "float8")
    util.create_column(cr, "account_bank_statement_line", "is_reconciled", "boolean", default=False)
    util.create_column(cr, "account_bank_statement_line", "foreign_currency_id", "int4")
    util.rename_field(cr, "account.bank.statement.line", "name", "payment_ref")
    for field_name in (
        "journal_currency_id",
        "move_name",
        "journal_entry_ids",
        "note",
        "account_id",
        "bank_account_id",
    ):
        util.remove_field(cr, "account.bank.statement.line", field_name)

    util.create_column(cr, "account_payment", "move_id", "int4")
    cr.execute("CREATE index ON account_payment(move_id)")
    util.create_column(cr, "account_payment", "destination_account_id", "int4")
    util.create_column(cr, "account_payment", "is_reconciled", "boolean", default=False)
    util.create_column(cr, "account_payment", "is_matched", "boolean", default=False)
    for field_name in ("company_id", "name", "state", "journal_id"):
        util.remove_column(cr, "account_payment", field_name)
    util.rename_field(cr, "account.payment", "partner_bank_account_id", "partner_bank_id")
    util.update_field_references(cr, "payment_date", "date", only_models=("account.payment",))
    for field_name in (
        "move_name",
        "payment_date",
        "communication",
        "payment_difference",
        "payment_difference_handling",
        "writeoff_account_id",
        "writeoff_label",
        "possible_bank_partner_ids",
        "partner_bank_account_id",
        "state_before_switch",
        "_suitable_journal_ids",
        "_payment_methods",
        "move_reconciled",
        "move_line_ids",
        "has_invoices",
        "invoice_ids",
        "destination_journal_id",
    ):
        util.remove_field(cr, "account.payment", field_name)

    # Don't replace the payment account by the outstanding account if any link to a statement line.
    # Match the same journal to manage correctly the internal transfers.
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_payment_pre_backup pay_backup
                SET no_replace_account = TRUE
                FROM account_move_line line
                WHERE line.payment_id = pay_backup.id
                AND line.statement_line_id IS NOT NULL
                AND line.journal_id = pay_backup.journal_id
            """,
            prefix="pay_backup.",
        ),
    )

    # ==== Migrate the bank statements ====

    # === account.bank.statement ===

    # Fix 'is_valid_balance_start' that is now stored.

    cr.execute(
        """
        WITH rows AS (
               SELECT st.id,
                      CASE
                         WHEN previous_st.balance_end_real IS NOT NULL
                            THEN ROUND(
                                st.balance_start - previous_st.balance_end_real,
                                cur.decimal_places
                            ) = 0
                         ELSE true
                      END AS flag
                 FROM account_bank_statement st
            LEFT JOIN account_bank_statement previous_st ON previous_st.id = st.previous_statement_id
                 JOIN account_journal aj ON aj.id = st.journal_id
            LEFT JOIN res_company cp ON cp.id = st.company_id
                 JOIN res_currency cur ON cur.id = COALESCE(aj.currency_id, cp.currency_id)
        )
        UPDATE account_bank_statement st
           SET is_valid_balance_start = r.flag
          FROM rows r
         WHERE r.id = st.id
    """
    )

    # === account.bank.statement.line ===

    # - The old 'currency_id' field becomes 'foreign_currency_id'.
    # - The new 'currency_id' field must contains the journal's currency or the company's currency.

    cr.execute(
        """
        UPDATE account_bank_statement_line st_line
        SET foreign_currency_id = st_line_backup.currency_id
        FROM account_bank_statement_line_pre_backup st_line_backup
        WHERE st_line_backup.id = st_line.id
    """
    )

    # the journal_id of a statement line is a related stored field to the journal_id
    # of the parent statement which is a required field.
    # to avoid using a possibly broken journal_id from statement lines, directly use the
    # journal_id from the parent statement.
    cr.execute(
        """
        UPDATE account_bank_statement_line st_line
           SET currency_id = COALESCE(journal.currency_id, comp.currency_id)
          FROM account_bank_statement_line_pre_backup st_line_backup
          JOIN account_bank_statement st ON st.id = st_line_backup.statement_id
          JOIN account_journal journal ON journal.id = st.journal_id
          JOIN res_company comp ON comp.id = COALESCE(st_line_backup.company_id, journal.company_id)
         WHERE st_line_backup.id = st_line.id
    """
    )

    # Fix the relational link between account.bank.statement.line & account.move.
    # Both are linked by a one2one (move_id in account.bank.statement.line & statement_line_id in account.move).
    # /!\ Take care about the fact some journal entry could be linked to multiple statement lines. This is the case for
    # some entries generated before the following fix:
    # https://github.com/odoo/odoo/commit/f08204c69c684a6614bbbebc834178355b4aad03
    # /!\ A statement could be reconciled with multiple black/blue lines in the reconciliation widget. In that case,
    # keep the auto generated move first. If not, keep the first move you found.
    mapping_queries = []

    # Retrieve the journal entry using the field set on the journal item using the liquidity account.
    # This query is probably the one that will do most of the job for regular reconciliation using the reconciliation
    # widget. It works for:
    # - matching a single blue line (payment).
    # - matching one or more black lines. In that case, a single payment will be generated.
    mapping_queries.append(
        """
        SELECT
            line.statement_line_id,
            MAX(line.move_id) as move_id
        FROM account_move_line line
        JOIN account_account account ON account.id = line.account_id
        JOIN account_bank_statement_line st_line ON st_line.id = line.statement_line_id
        WHERE st_line.move_id IS NULL
        AND account.internal_type = 'liquidity'
        GROUP BY line.statement_line_id
        HAVING COUNT(DISTINCT line.move_id) = 1
        """
    )

    # Retrieve the right journal entry based on the move_name stored on the statement line.
    # It works for all reconciliation having at least one black line.
    mapping_queries.append(
        """
        SELECT
            line.statement_line_id,
            MAX(line.move_id) as move_id
        FROM account_move_line line
        JOIN account_account account ON account.id = line.account_id
        JOIN account_move move ON move.id = line.move_id
        JOIN account_bank_statement_line st_line ON st_line.id = line.statement_line_id
        WHERE st_line.move_id IS NULL
        AND account.internal_type = 'liquidity'
        AND move.name = line.move_name
        AND line.move_name != '/'
        AND line.move_name IS NOT NULL
        GROUP BY line.statement_line_id
        HAVING COUNT(DISTINCT line.move_id) = 1
        """
    )

    # Keep the first journal entry found on the same journal. This is needed when the statement line is reconciled with
    # multiple blue lines (payments).
    mapping_queries.append(
        """
        SELECT
            line.statement_line_id,
            MAX(line.move_id) as move_id
        FROM account_move_line line
        JOIN account_bank_statement_line st_line ON st_line.id = line.statement_line_id
        JOIN account_bank_statement_line_pre_backup st_line_backup ON st_line_backup.id = st_line.id
        WHERE st_line.move_id IS NULL
        AND st_line_backup.journal_id = line.journal_id
        GROUP BY line.statement_line_id
        """
    )

    # Keep the first journal entry found as fallback.
    mapping_queries.append(
        """
        SELECT
            line.statement_line_id,
            MAX(line.move_id) as move_id
        FROM account_move_line line
        JOIN account_bank_statement_line st_line ON st_line.id = line.statement_line_id
        WHERE st_line.move_id IS NULL
        GROUP BY line.statement_line_id
        """
    )

    for mapping in mapping_queries:
        cr.execute(
            f"""
            WITH mapping AS ({mapping})

            UPDATE account_bank_statement_line st_line
            SET move_id = mapping.move_id,
                is_reconciled = TRUE
            FROM mapping
            WHERE id = mapping.statement_line_id AND st_line.move_id IS NULL
            """
        )

    cr.execute(
        """
        UPDATE account_move
        SET statement_line_id = st_line.id
        FROM account_bank_statement_line st_line
        WHERE st_line.move_id = account_move.id
    """
    )

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move
                   SET statement_line_id = account_bank_statement_line.id
                  FROM account_bank_statement_line
                 WHERE account_bank_statement_line.move_id = account_move.id
                   AND account_move.statement_line_id IS NULL
            """,
            prefix="account_move.",
        ),
    )

    # Update existing account.move.

    cr.execute(
        """
        UPDATE account_move move
        SET currency_id = COALESCE(journal.currency_id, company.currency_id),
            partner_id = st_line_backup.partner_id,
            commercial_partner_id = st_line_backup.partner_id,
            partner_bank_id = st_line_backup.bank_account_id,
            journal_id = st_line_backup.journal_id,
            ref = st_line_backup.ref,
            narration = st_line_backup.note,
            company_id = st_line_backup.company_id
        FROM account_bank_statement_line_pre_backup st_line_backup
        JOIN account_bank_statement_line st_line ON st_line.id = st_line_backup.id
        JOIN account_journal journal ON journal.id = st_line_backup.journal_id
        JOIN res_company company ON company.id = journal.company_id
        WHERE move.id = st_line.move_id
    """
    )

    # ==== Migrate the payments ====

    # Fix the relational link between account.payment & account.move.
    # Both are linked by a one2one (move_id in account.payment & payment_id in account.move).

    # At least one move line is still linked to the payment on the same journal.
    # In case of internal transfer, only one move will be linked.
    cr.execute(
        """
        WITH mapping AS (
            SELECT
                line.payment_id,
                MAX(line.move_id) as move_id
            FROM account_move_line line
            JOIN account_payment_pre_backup pay_backup ON
                pay_backup.id = line.payment_id
                AND
                line.journal_id = pay_backup.journal_id
            GROUP BY line.payment_id
            HAVING COUNT(DISTINCT line.move_id) = 1
        )

        UPDATE account_payment pay
        SET move_id = mapping.move_id
        FROM mapping
        WHERE pay.id = mapping.payment_id
    """
    )

    # At least one move line is still linked to the payment but not necessarily on the same journal.
    cr.execute(
        """
        WITH mapping AS (
            SELECT
                line.payment_id,
                MAX(line.move_id) as move_id
            FROM account_move_line line
            JOIN account_payment_pre_backup pay_backup ON pay_backup.id = line.payment_id
            JOIN account_payment pay ON pay.id = line.payment_id
            WHERE pay.move_id IS NULL
            GROUP BY line.payment_id
            HAVING COUNT(DISTINCT line.move_id) = 1
        )

        UPDATE account_payment pay
        SET move_id = mapping.move_id
        FROM mapping
        WHERE pay.id = mapping.payment_id
    """
    )

    # Corner case: no link left between account.payment & account.move.line due to manual
    # user edition.
    cr.execute(
        """
        WITH mapping AS (
            SELECT
                pay.id AS payment_id,
                move.id AS move_id
            FROM account_payment_pre_backup pay_backup
            JOIN account_payment pay ON pay.id = pay_backup.id
            JOIN account_move move ON move.name = pay_backup.move_name
            LEFT JOIN account_payment pay2 ON pay2.move_id = move.id
            WHERE move.state IN ('posted', 'cancel')
            AND move.statement_line_id IS NULL
            AND pay_backup.move_name IS NOT NULL
            AND pay_backup.move_name != '/'
            AND pay.move_id IS NULL
            AND pay_backup.journal_id = move.journal_id
            AND pay_backup.partner_id = move.partner_id
            AND pay_backup.currency_id = move.currency_id
            AND pay2.move_id IS NULL
        )

        UPDATE account_payment pay
        SET move_id = mapping.move_id
        FROM mapping
        WHERE pay.id = mapping.payment_id
    """
    )

    util.create_index("account_move_payment_id_index", "account_move", "payment_id")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_move
                   SET payment_id = account_payment.id
                  FROM account_payment
                 WHERE account_payment.move_id = account_move.id
                   AND account_move.payment_id IS NULL
            """,
            prefix="account_move.",
        ),
    )

    # Update existing account.move.

    cr.execute(
        """
        UPDATE account_move move
        SET partner_id = pay_backup.partner_id,
            commercial_partner_id = partner.commercial_partner_id,
            currency_id = pay_backup.currency_id,
            partner_bank_id = pay_backup.partner_bank_account_id,
            is_move_sent = (move.id = pay.move_id and pay_backup.state in ('sent', 'reconciled'))
        FROM account_payment_pre_backup pay_backup
        JOIN account_payment pay ON pay.id = pay_backup.id
        LEFT JOIN res_partner partner ON partner.id = pay_backup.partner_id
        JOIN account_journal journal ON journal.id = pay_backup.journal_id
        JOIN res_company comp ON comp.id = journal.company_id
        WHERE move.id = pay.move_id
    """
    )

    # Fix newly added computed field: destination_account_id.
    # This field will be computed differently depending the payment already has a journal entry or not.
    # - If there is a journal entry, pick the one set on the account.move.line.
    # - If there is no journal entry, do the '_compute_destination_account_id' in SQL.
    #   - A partner is set != the one set on the company: need a receivable/payable account.
    #   - A partner is set = the one set on the company: need the internal transfer account set on the company.
    #   - No partner: set the first available receivable/payable account.

    # Payments being an internal transfer.
    cr.execute(
        """
        UPDATE account_payment pay
        SET destination_account_id = comp.transfer_account_id
        FROM account_payment_pre_backup pay_backup
        JOIN account_journal journal ON journal.id = pay_backup.journal_id
        JOIN res_company comp ON comp.id = journal.company_id
        WHERE pay_backup.id = pay.id
        AND journal.id = pay_backup.journal_id
        AND pay.is_internal_transfer
        AND pay.destination_account_id IS NULL
    """
    )

    # Compute 'destination_account_id' from existing moves.
    cr.execute(
        """
        WITH account_mapping AS (
            SELECT account_id, line.payment_id
            FROM account_move_line line
            WHERE line.account_internal_type IN ('receivable', 'payable')
            AND line.payment_id IS NOT NULL
        )

        UPDATE account_payment
        SET destination_account_id = account_mapping.account_id
        FROM account_mapping
        WHERE account_mapping.payment_id = account_payment.id
        AND destination_account_id IS NULL
        AND account_payment.move_id IS NOT NULL
        AND NOT account_payment.is_internal_transfer
    """
    )

    # Compute 'destination_account_id' from partner's properties.
    for partner_type, property_name in [
        ("customer", "property_account_receivable_id"),
        ("supplier", "property_account_payable_id"),
    ]:
        cr.execute(
            """
            WITH default_properties AS (
                SELECT
                    res_partner.id AS partner_id,
                    default_prop.company_id,
                    SPLIT_PART(default_prop.value_reference, ',', 2)::int AS account_id
                FROM res_partner, ir_model_fields field
                LEFT JOIN ir_property default_prop ON default_prop.fields_id = field.id
                WHERE field.name = %(property_name)s
                AND field.model = 'res.partner'
                AND SPLIT_PART(default_prop.value_reference, ',', 1) = 'account.account'
                AND default_prop.res_id IS NULL
            ),
            properties AS (
                SELECT
                    res_partner.id AS partner_id,
                    prop.company_id,
                    SPLIT_PART(prop.value_reference, ',', 2)::int AS account_id
                FROM res_partner, ir_model_fields field
                LEFT JOIN ir_property prop ON prop.fields_id = field.id
                WHERE field.name = %(property_name)s
                AND field.model = 'res.partner'
                AND SPLIT_PART(prop.value_reference, ',', 1) = 'account.account'
                AND prop.res_id = 'res.partner,' || res_partner.id
            )

            UPDATE account_payment pay
            SET destination_account_id = COALESCE(prop.account_id, default_prop.account_id)
            FROM account_payment_pre_backup pay_backup
            JOIN account_journal journal ON journal.id = pay_backup.journal_id
            JOIN res_partner partner ON partner.id = pay_backup.partner_id
            LEFT JOIN default_properties default_prop ON default_prop.partner_id = partner.commercial_partner_id
            LEFT JOIN properties prop ON prop.partner_id = partner.commercial_partner_id AND prop.company_id = pay_backup.company_id
            WHERE pay_backup.id = pay.id
            AND pay.destination_account_id IS NULL
            AND NOT pay.is_internal_transfer
            AND pay.partner_type = %(partner_type)s
        """,
            {"property_name": property_name, "partner_type": partner_type},
        )

    # Set default accounts to 'destination_account_id'.
    cr.execute(
        """
        WITH all_accounts AS (
            SELECT
                id AS account_id,
                company_id,
                internal_type,
                row_number() OVER (PARTITION BY company_id, internal_type ORDER BY code) AS row_number
            FROM account_account
            WHERE internal_type IN ('receivable', 'payable')
            AND NOT deprecated
        ),
        default_accounts AS (
            SELECT
                all_accounts.account_id,
                all_accounts.company_id,
                all_accounts.internal_type
            FROM all_accounts
            WHERE all_accounts.row_number = 1
        )

        UPDATE account_payment pay
        SET destination_account_id = default_accounts.account_id
        FROM account_payment_pre_backup pay_backup
        JOIN account_journal journal ON journal.id = pay_backup.journal_id
        JOIN default_accounts ON default_accounts.company_id = journal.company_id
        WHERE pay_backup.id = pay.id
        AND NOT pay.is_internal_transfer
        AND pay.partner_id IS NULL
        AND pay.destination_account_id IS NULL
        AND default_accounts.internal_type = CASE WHEN pay.partner_type = 'customer' THEN 'receivable' ELSE 'payable' END
    """
    )

    # Compute 'is_reconciled'.

    cr.execute(
        """
        WITH residual_per_pay AS (
              SELECT pay.id AS payment_id
                FROM account_payment pay
                JOIN account_move move ON move.payment_id = pay.id
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_account account ON account.id = line.account_id
               WHERE move.id = pay.move_id
                 AND account.reconcile IS TRUE
                 AND line.account_id = pay.destination_account_id
            GROUP BY pay.id
              HAVING COALESCE(SUM(
                    CASE WHEN line.currency_id IS NULL
                      THEN line.amount_residual
                      ELSE line.amount_residual_currency
                    END
              ), 0.0) = 0.0
        )
        UPDATE account_payment
           SET is_reconciled = true
          FROM residual_per_pay
         WHERE residual_per_pay.payment_id = account_payment.id
    """
    )

    # Compute 'is_matched'.

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE account_payment pay
                SET is_matched = pay_backup.no_replace_account
                FROM account_payment_pre_backup pay_backup
                WHERE pay.id = pay_backup.id
            """,
            prefix="pay.",
        ),
    )

    # We can not update fields while 'restrict_mode_hash_table' is True and 'type' in ('cash', 'bank').
    # That issue already raised in v13.0 so its already fix at https://github.com/odoo/upgrade/pull/2185/files
    # But what if that issue again raised in migrating v13 -> v14.0 Database.
    # Already discuss on upgrade issue (https://github.com/odoo/upgrade/issues/2198) about this problem.
    cr.execute(
        """
        UPDATE account_journal
           SET secure_sequence_id = NULL,
               restrict_mode_hash_table = false
         WHERE (secure_sequence_id IS NOT NULL
            OR restrict_mode_hash_table = true)
           AND type IN ('cash','bank')
        """
    )

    # ==== Check ====

    cr.execute("SELECT id FROM account_payment WHERE destination_account_id IS NULL")
    for payment_id in cr.fetchall():
        _logger.error("Missing destination_account_id on account.payment (id=%s)", payment_id)
