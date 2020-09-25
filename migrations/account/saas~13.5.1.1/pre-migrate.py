# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
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
        util.update_field_references(
            cr, f"default_{infix}_account_id", "default_account_id", only_models=("account.journal",)
        )

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
