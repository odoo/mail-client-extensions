# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = {
        'view_order_form_inherit': 'view_order_form_inherit_sale_stock',
        'view_order_line_tree_inherit': 'view_order_line_tree_inherit_sale_stock',
        'view_invoice_form_inherit': 'invoice_form_inherit_sale_stock',
        'report_invoice_incoterm': 'report_invoice_document_inherit_sale_stock',
    }
    for f, t in renames.items():
        util.rename_xmlid(cr, 'sale_stock.' + f, 'sale_stock.' + t)

    todel = util.splitlines("""
        view_picking_internal_search_inherit
    """)
    for v in todel:
        util.remove_view(cr, 'sale_stock.' + v)
