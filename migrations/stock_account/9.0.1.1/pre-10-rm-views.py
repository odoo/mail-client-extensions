# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        view_picking_inherit_tree2
        view_move_form_inherit
        view_procurement_rule_form_stockaccount_inherit
        view_pusht_rule_form_stockaccount_inherit
        view_move_picking_from_stockaccount_inherit
        view_stock_return_picking_form_inherit
    """)
    for v in views:
        util.remove_view(cr, 'stock_account.' + v)
