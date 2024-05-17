# -*- coding: utf-8 -*-
import psycopg2

from odoo.tools.misc import ignore

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.create_column(cr, "account_account", "is_off_balance", "boolean")

    query = "UPDATE account_account SET is_off_balance = (internal_group='off_balance')"
    util.explode_execute(cr, query, table="account_account")

    util.create_column(cr, "validate_account_move", "force_post", "boolean")

    # Res_company
    util.create_column(cr, "res_company", "expense_currency_exchange_account_id", "int4")
    util.create_column(cr, "res_company", "income_currency_exchange_account_id", "int4")
    cr.execute(
        """
            UPDATE res_company
               SET expense_currency_exchange_account_id = journal.default_debit_account_id,
                   income_currency_exchange_account_id = journal.default_credit_account_id
              FROM account_journal journal
             WHERE journal.id = res_company.currency_exchange_journal_id
        """
    )

    # Account_payment
    util.create_column(cr, "account_payment_method", "sequence", "int4")
    cr.execute("UPDATE account_payment_method SET sequence = id")

    # Account_journal
    util.create_column(cr, "account_journal", "default_account_id", "int4")
    for infix in {"credit", "debit"}:
        util.update_field_usage(cr, "account.journal", f"default_{infix}_account_id", "default_account_id")

    cr.execute(
        """
            UPDATE account_journal
               SET default_account_id = COALESCE(default_credit_account_id, default_debit_account_id)
        """
    )
    util.remove_field(cr, "account.journal", "default_debit_account_id")
    util.remove_field(cr, "account.journal", "default_credit_account_id")

    # Setup_wizard
    util.remove_field(cr, "account.setup.bank.manual.config", "new_journal_code")
    util.remove_field(cr, "account.setup.bank.manual.config", "related_acc_type")

    util.remove_view(cr, "account.dashboard_onboarding_company_step")

    # ===========================================================
    # Currency on all account.move.line (PR:50711 & 10394)
    # ===========================================================

    util.remove_field(cr, "account.move.line", "always_set_currency_id")
    util.remove_constraint(cr, "account_move_line", "account_move_line_check_amount_currency_balance_sign")

    # Some databases have incorrect balance computation, off by a small fraction, for instance:
    # 13.915 - 0.0 = 13.92
    # We correct this error, because otherwise the constraint below is not going to be added.
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line
           SET balance = debit - credit
         WHERE balance != debit - credit
        """,
        table="account_move_line",
    )

    util.explode_execute(
        cr,
        """
        UPDATE account_move_line
           SET currency_id = company_currency_id,
               amount_currency = balance,
               amount_residual_currency = amount_residual
         WHERE currency_id IS NULL
        """,
        table="account_move_line",
    )

    # Prevent inconsistencies in others scripts by adding the updated constraint manually (if possible)
    with ignore(psycopg2.Error), util.savepoint(cr):
        cr.execute(
            """
                ALTER TABLE account_move_line
                ADD CONSTRAINT account_move_line_check_amount_currency_balance_sign
                CHECK(
                    (
                        (currency_id != company_currency_id)
                        AND
                        (
                            (debit - credit <= 0 AND amount_currency <= 0)
                            OR
                            (debit - credit >= 0 AND amount_currency >= 0)
                        )
                    )
                    OR
                    (
                        currency_id = company_currency_id
                        AND
                        ROUND(debit - credit - amount_currency, 2) = 0
                    )
                )
            """
        )

    # ===========================================================
    # Fiscal country field on companies (PR 55308 & 12156)
    # ===========================================================
    util.create_column(cr, "res_company", "account_tax_fiscal_country_id", "int4")

    # If a fiscal country was set with the dedicated config parameter, use it; else use the company's country.
    cr.execute(
        """
            UPDATE res_company
               SET account_tax_fiscal_country_id = COALESCE(parameter_country.id, company_partner.country_id)
              FROM res_partner company_partner
              JOIN res_company company ON company_partner.id = company.partner_id
         LEFT JOIN ir_config_parameter fiscal_country_param
                ON fiscal_country_param.key = CONCAT('account_fiscal_country_', company.id)
         LEFT JOIN res_country parameter_country ON LOWER(parameter_country.code) = LOWER(fiscal_country_param.value)
             WHERE res_company.id = company.id
        """
    )

    # Remove the fiscal country config parameters; now useless.
    cr.execute("DELETE FROM ir_config_parameter WHERE key LIKE 'account_fiscal_country_%'")

    # Replace the old related fields which pointed towards company country for use in taxes
    util.rename_field(cr, "account.move.line", "country_id", "tax_fiscal_country_id")
    util.rename_field(cr, "account.tax", "country_id", "tax_fiscal_country_id")
    util.rename_field(cr, "account.tax.repartition.line", "country_id", "tax_fiscal_country_id")

    # ===========================================================
    # Fusion of automatic entry wizards (PR:48651)
    # ===========================================================
    util.rename_field(cr, "res.company", "accrual_default_journal_id", "automatic_entry_default_journal_id")
    util.remove_model(cr, "account.accrual.accounting.wizard")
    util.remove_model(cr, "account.transfer.wizard")
    util.remove_column(cr, "account_move_line", "account_internal_type")
    util.remove_record(cr, "account.action_accrual_entry")
    util.remove_record(cr, "account.action_move_transfer_accounts")

    # ===========================================================
    # Reconciliation model improvements (PR:55031)
    # ===========================================================
    util.create_column(cr, "account_reconcile_model", "active", "boolean", default=True)
    for table in ("account_reconcile_model", "account_reconcile_model_template"):
        util.create_column(cr, table, "matching_order", "varchar", default="old_first")
        util.create_column(cr, table, "match_text_location_label", "boolean", default=True)
        util.create_column(cr, table, "match_text_location_note", "boolean", default=False)
        util.create_column(cr, table, "match_text_location_reference", "boolean", default=False)

    util.remove_view(cr, "account.report_invoice_document_with_payments")

    # ===========================================================
    # Tour refactor (PR:55624)
    # ===========================================================
    util.rename_field(cr, "res.company", *eb("account_onboarding_{sample,create}_invoice_state"))
    util.remove_view(cr, "account.onboarding_sample_invoice_step")
    util.remove_view(cr, "account.email_compose_onboarding_sample_invoice")
    util.remove_record(cr, "account.action_open_account_onboarding_sample_invoice")

    # Now a dynamic view. See https://github.com/odoo/odoo/pull/56080
    cr.execute("DROP VIEW IF EXISTS account_invoice_report CASCADE")
