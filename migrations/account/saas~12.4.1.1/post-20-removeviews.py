# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    move_line_map = (
        (util.ref(cr, "account.view_invoice_line_tree"), util.ref(cr, "account.view_move_line_tree")),
        (util.ref(cr, "account.view_invoice_line_form"), util.ref(cr, "account.view_move_line_form")),
    )
    move_map = (
        (util.ref(cr, "account.invoice_tree"), util.ref(cr, "account.view_move_tree")),
        (util.ref(cr, "account.invoice_kanban"), util.ref(cr, "account.view_account_move_kanban")),
        (util.ref(cr, "account.invoice_form"), util.ref(cr, "account.view_move_form")),
        (util.ref(cr, "account.invoice_tree_with_onboarding"), util.ref(cr, "account.view_invoice_tree")),
    )
    query = """
           UPDATE ir_ui_view view
              SET model = %s,
                  inherit_id = %s
             FROM ir_model_data imd
            WHERE imd.res_id = view.id
              AND imd.model = 'ir.ui.view'
             AND imd.module = 'studio_customization'
              AND view.model = %s
              AND view.inherit_id = %s
    """
    for old, new in move_map:
        cr.execute(query, ["account.move", new, "account.invoice", old])
    for old, new in move_line_map:
        cr.execute(query, ["account.move.line", new, "account.invoice.line", old])
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
    util.remove_view(cr, "account.invoice_form")
