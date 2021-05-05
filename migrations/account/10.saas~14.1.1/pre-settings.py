# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account.view_account_config_settings")

    fields = util.splitlines(
        """
        has_default_company
        excpects_chart_of_accounts
        company_footer
        sale_tax_id
        purchase_tax_id
        sale_tax_rate
        purchase_tax_rate

        bank_account_code_prefix
        cash_account_code_prefix
        template_transfer_account_id

        complete_tax_set
        period_lock_date

        currency_exchange_journal_id

        module_account_tax_cash_basis
        overdue_msg

        # this field change type (0/1 selection -> boolean)
        group_warning_account
        """
    )
    for f in fields:
        util.remove_field(cr, "account.config.settings", f)

    moved = util.splitlines(
        """
        use_anglo_saxon
        transfer_account_id
        tax_cash_basis_journal_id
        fiscalyear_last_day
        fiscalyear_last_month
        """
    )
    if util.module_installed(cr, "account_accountant"):
        for m in moved:
            util.move_field_to_module(cr, "account.config.settings", m, "account", "account_accountant")
    else:
        for m in moved:
            util.remove_field(cr, "account.config.settings", m)
