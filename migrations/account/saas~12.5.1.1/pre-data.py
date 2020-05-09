# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("account.account_payment_term_{net,30days}"))
    util.rename_xmlid(cr, *eb("account.account_payment_term{,_end_following_month}"))

    util.remove_record(cr, "account.act_account_move_to_account_move_line_open")
    util.remove_record(cr, "account.action_open_account_onboarding_invoice_layout")
    util.remove_record(cr, "account.act_account_journal_2_account_bank_statement")
    util.remove_record(cr, "account.action_view_account_bnk_stmt_cashbox")
    util.remove_record(cr, "account.product_product_action")
    util.remove_record(cr, "account.action_open_partner_analytic_accounts")

    util.remove_view(cr, "account.account_invoice_onboarding_invoice_layout_form")
    util.remove_view(cr, "account.portal_invoice_chatter")
    util.remove_view(cr, "account.product_product_view_tree")
    util.remove_view(cr, "account.partner_view_button_contracts_count")
    util.remove_view(cr, "account.partner_view_buttons")
    util.remove_view(cr, "account.view_partner_property_form")
    util.remove_view(cr, "account.account_tag_view_form")
    util.remove_view(cr, "account.view_account_bnk_stmt_cashbox_footer")
    util.remove_view(cr, "account.view_account_bnk_stmt_cashbox")

    util.force_noupdate(cr, "account.open_account_journal_dashboard_kanban", False)
