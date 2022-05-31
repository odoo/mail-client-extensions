# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "account_fiscal_country_id", "account_accountant", "account")

    util.remove_view(cr, "account.report_journal")
    util.remove_model(cr, "report.account.report_journal")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.menu_finance_entries_accounting_journals"),
            util.ref(cr, "account.menu_action_account_moves_journal_sales"),
            util.ref(cr, "account.menu_action_account_moves_journal_purchase"),
            util.ref(cr, "account.menu_action_account_moves_journal_bank_cash"),
            util.ref(cr, "account.menu_action_account_moves_journal_misc"),
            util.ref(cr, "account.menu_finance_entries_accounting_ledgers"),
            util.ref(cr, "account.menu_action_account_moves_ledger_general"),
            util.ref(cr, "account.menu_action_account_moves_ledger_partner"),
        ],
    )
