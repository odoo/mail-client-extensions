# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # =======================================================================================
    # Remove stuff
    # =======================================================================================

    # Menus
    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.menu_action_invoice_tree1"),
            util.ref(cr, "account.menu_action_invoice_out_refund"),
            util.ref(cr, "account.menu_action_invoice_tree2"),
            util.ref(cr, "account.menu_action_invoice_in_refund"),
        ],
    )

    # Views (account_voucher)
    if util.ENVIRON["account_voucher_installed"]:
        util.remove_view(cr, "account.view_voucher_tree")
        util.remove_view(cr, "account.view_voucher_tree_purchase")
        util.remove_view(cr, "account.view_voucher_kanban")
        util.remove_view(cr, "account.view_voucher_line_form")
        util.remove_view(cr, "account.view_voucher_line_tree")
        util.remove_view(cr, "account.view_voucher_filter")
        util.remove_view(cr, "account.account_cash_statement_graph")
        util.remove_view(cr, "account.view_voucher_filter_vendor")
        util.remove_view(cr, "account.view_voucher_filter_sale")
        util.remove_view(cr, "account.view_sale_receipt_form")
        util.remove_view(cr, "account.view_purchase_receipt_form")

    # Views to be reloaded by the ORM as the whole view changed.
    util.remove_view(cr, "account.view_move_form")
    util.remove_view(cr, "account.view_account_invoice_filter")

    # Views (account_invoice_refund)
    util.remove_view(cr, "account.view_account_invoice_refund")

    # Views (account_invoice_confirm)
    util.remove_view(cr, "account.account_invoice_confirm_view")

    # Security rules (noupdate block)
    util.remove_record(cr, "account.invoice_comp_rule")
    util.remove_record(cr, "account.account_invoice_line_comp_rule")
    util.remove_record(cr, "account.tax_report_comp_rule")
    util.remove_record(cr, "account.account_invoice_rule_portal")
    util.remove_record(cr, "account.account_invoice_line_rule_portal")

    # Force update of record rules linked to invoices
    cr.execute(
        """
        WITH rules AS (
            SELECT r.id
              FROM ir_rule r
              JOIN ir_model m ON r.model_id=m.id
             WHERE m.model in ('account.invoice','account.invoice.line','account.voucher')
        )
        UPDATE ir_model_data
           SET noupdate=FALSE
          FROM rules
         WHERE model='ir.rule'
           AND res_id=rules.id
        """
    )

    util.remove_field(cr, "res.config.settings", "group_products_in_bills")
    util.remove_model(cr, "account.invoice.confirm")
    util.remove_model(cr, "account.invoice.refund")
