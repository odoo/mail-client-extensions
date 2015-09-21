# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'sale_stock.view_order_form_inherit',
                          'sale_stock.view_order_form_inherit_sale_stock')   # noqa

    todel = util.splitlines("""
        view_picking_internal_search_inherit
    """)
    for v in todel:
        util.remove_view(cr, 'sale_stock.' + v)
