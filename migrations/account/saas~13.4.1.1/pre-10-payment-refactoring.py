# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-13.4.1.1." + __name__)


def migrate(cr, version):
    cr.execute('''
        UPDATE account_bank_statement_line st_line
           SET move_name = NULL
         WHERE move_name IN (SELECT name FROM account_move)
    ''')

    cr.execute('''
        UPDATE account_bank_statement_line st_line
           SET move_name = NULL
          FROM account_bank_statement_line older_st_line
         WHERE st_line.move_name = older_st_line.move_name
           AND st_line.id > older_st_line.id
    ''')

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

    util.create_column(cr, "account_bank_statement", "is_valid_balance_start", "boolean")
    util.remove_field(cr, "account.bank.statement", "accounting_date")

    util.create_column(cr, "account_bank_statement_line", "move_id", "int4")
    cr.execute("CREATE index ON account_bank_statement_line(move_id)")
    util.create_column(cr, "account_bank_statement_line", "is_reconciled", "boolean")
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
    util.create_column(cr, "account_payment", "is_reconciled", "boolean")
    util.create_column(cr, "account_payment", "is_matched", "boolean")
    for field_name in ("company_id", "name", "state"):
        util.remove_column(cr, "account_payment", field_name)
    util.rename_field(cr, "account.payment", "partner_bank_account_id", "partner_bank_id")
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

    # ==== Migrate the bank statements ====

    # === account.bank.statement ===

    # Fix 'is_valid_balance_start' that is now stored.

    cr.execute(
        """
        UPDATE account_bank_statement st
        SET is_valid_balance_start = (st.balance_start = previous_st.balance_end_real)
        FROM account_bank_statement previous_st
        WHERE previous_st.id = st.previous_statement_id
        AND st.balance_start = previous_st.balance_end_real
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

    cr.execute(
        """
        UPDATE account_bank_statement_line st_line
        SET currency_id = COALESCE(journal.currency_id, comp.currency_id)
        FROM account_bank_statement_line_pre_backup st_line_backup
        JOIN account_journal journal ON journal.id = st_line_backup.journal_id
        JOIN res_company comp ON comp.id = st_line_backup.company_id
        WHERE st_line_backup.id = st_line.id
    """
    )

    # Fix the relational link between account.bank.statement.line & account.move.
    # Both are linked by a one2one (move_id in account.bank.statement.line & statement_line_id in account.move).

    cr.execute(
        """
        WITH mapping AS (
            SELECT
                line.statement_line_id,
                MAX(DISTINCT line.move_id) as move_id,
                COUNT(DISTINCT line.move_id) AS nbr
            FROM account_move_line line
            WHERE line.statement_line_id IS NOT NULL
            GROUP BY line.statement_line_id
        )

        UPDATE account_bank_statement_line
        SET move_id = mapping.move_id,
            is_reconciled = TRUE
        FROM mapping
        WHERE id = mapping.statement_line_id
        AND mapping.nbr = 1;
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

    cr.execute(
        """
        WITH mapping AS (
            SELECT
                line.payment_id,
                MAX(DISTINCT line.move_id) as move_id,
                COUNT(DISTINCT line.move_id) AS nbr
            FROM account_move_line line
            JOIN account_payment_pre_backup pay_backup ON pay_backup.id = line.payment_id
            WHERE line.journal_id = pay_backup.journal_id
            GROUP BY line.payment_id
        )

        UPDATE account_payment
        SET move_id = mapping.move_id
        FROM mapping
        WHERE id = mapping.payment_id
        AND mapping.nbr = 1
    """
    )

    cr.execute(
        """
        UPDATE account_move
        SET payment_id = pay.id
        FROM account_payment pay
        WHERE pay.move_id = account_move.id
    """
    )

    # Update existing account.move.

    cr.execute(
        """
        UPDATE account_move move
        SET partner_id = pay_backup.partner_id,
            commercial_partner_id = partner.commercial_partner_id,
            currency_id = pay_backup.currency_id
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
            SELECT
                pay.id AS payment_id,
                COALESCE(SUM(
                    CASE WHEN line.currency_id IS NULL
                    THEN line.amount_residual
                    ELSE line.amount_residual_currency END
                ), 0.0) AS residual
            FROM account_payment pay
            JOIN account_move move ON move.payment_id = pay.id
            JOIN account_move_line line ON line.move_id = move.id
            JOIN account_account account ON account.id = line.account_id
            WHERE move.id = pay.move_id
            AND account.reconcile IS TRUE
            AND line.account_id = pay.destination_account_id
            GROUP BY pay.id
        )

        UPDATE account_payment
        SET is_reconciled = (residual_per_pay.residual = 0.0)
        FROM residual_per_pay
        WHERE residual_per_pay.payment_id = account_payment.id
    """
    )

    cr.execute(
        """
        UPDATE account_payment
        SET is_reconciled = FALSE
        WHERE is_reconciled IS NULL
    """
    )

    # Compute 'is_matched'.

    cr.execute(
        """
        UPDATE account_payment pay
        SET is_matched = (move.statement_line_id IS NOT NULL)
        FROM account_move move
        WHERE pay.move_id = move.id
    """
    )

    cr.execute(
        """
        UPDATE account_payment
        SET is_matched = FALSE
        WHERE is_matched IS NULL
    """
    )

    # ==== Check ====

    cr.execute("SELECT id FROM account_payment WHERE destination_account_id IS NULL")
    for payment_id in cr.fetchall():
        _logger.error("Missing destination_account_id on account.payment (id=%s)", payment_id)
