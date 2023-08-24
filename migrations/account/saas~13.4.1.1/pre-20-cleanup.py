# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    # ===========================================================
    # Action Cleanup (PR: 46110 & 8706)
    # ===========================================================
    to_remove_list = [
        "action_bank_statement_draft_tree",
        "action_account_template_form",
        "action_account_fiscal_position_template_form",
        "action_move_line_select_by_partner",
        "action_move_line_select_tax_audit",
        "action_move_line_graph",
        "action_move_line_graph_posted",
        "action_account_common_menu",
        "action_product_default_list",
        "actions_account_fiscal_year",
    ]
    to_move_list = [
        "group_fiscal_year",
        "access_account_fiscal_year_readonly",
        "account_tag_action",
        "action_account_group_tree",
        "action_tax_group",
    ]

    for record in to_remove_list:
        util.remove_record(cr, "account.%s" % record)

    views = """
        action_account_fiscal_year_form
        action_account_fiscal_year_search
        action_account_fiscal_year_tree

        view_account_payment_form_multi
        view_account_payment_invoice_form
    """
    for view in util.splitlines(views):
        util.remove_view(cr, f"account.{view}")

    if util.module_installed(cr, "account_accountant"):
        for record in to_move_list:
            util.rename_xmlid(cr, *eb("account{,_accountant}.%s" % record))

        util.move_field_to_module(cr, "res.config.settings", "group_fiscal_year", *eb("account{,_accountant}"))
        util.move_model(cr, "account.fiscal.year", *eb("account{,_accountant}"))
    else:
        for record in to_move_list:
            util.remove_record(cr, "account.%s" % record)

        util.remove_field(cr, "res.config.settings", "group_fiscal_year")
        util.remove_model(cr, "account.fiscal.year")

    for seq in "customer_invoice customer_refund supplier_invoice supplier_refund transfer".split():
        util.delete_unused(cr, f"account.sequence_payment_{seq}")
