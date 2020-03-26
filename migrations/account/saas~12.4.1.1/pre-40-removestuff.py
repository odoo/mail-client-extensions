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

    # Views (account_invoice)
    util.remove_view(cr, "account.view_invoice_line_calendar")
    util.remove_view(cr, "account.view_invoice_pivot")
    util.remove_view(cr, "account.view_invoice_graph")
    util.remove_view(cr, "account.account_invoice_view_activity")
    util.remove_view(cr, "account.view_invoice_line_tree")
    util.remove_view(cr, "account.view_invoice_line_form")
    util.remove_view(cr, "account.view_invoice_tax_tree")
    util.remove_view(cr, "account.view_invoice_tax_form")
    util.remove_view(cr, "account.invoice_tree")
    util.remove_view(cr, "account.invoice_tree_with_onboarding")
    util.remove_view(cr, "account.invoice_kanban")
    util.remove_view(cr, "account.invoice_supplier_tree")
    util.remove_view(cr, "account.invoice_supplier_form")
    util.remove_view(cr, "account.view_account_invoice_filter")

    # View (account_move) to be reloaded by the ORM as the whole view changed.
    util.remove_view(cr, "account.view_move_form")

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
        UPDATE ir_model_data
           SET noupdate=FALSE
         WHERE model='ir.rule'
           AND res_id in (SELECT id
                           FROM ir_rule
                          WHERE model_id in (SELECT id
                                               FROM ir_model
                                              WHERE model in ('account.invoice',
                                                              'account.invoice.line',
                                                              'account.voucher')
                                            )
                         )
        """
    )
