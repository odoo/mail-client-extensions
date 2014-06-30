# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.new_module_dep(cr, 'product', 'report')

    util.remove_module(cr, 'process')

    # Remove stock_location and stock_no_auto_picking
    util.remove_module(cr, 'stock_location')
    util.remove_module(cr, 'stock_no_auto_picking')

    # Inverse dependency of procurement from stock
    util.remove_module_deps(cr, 'procurement', ('stock',))
    util.new_module_dep(cr, 'stock', 'procurement')

    # Add dependencies from stock on web modules
    util.new_module_dep(cr, 'stock', 'web_kanban_gauge')
    util.new_module_dep(cr, 'stock', 'web_kanban_sparkline')
    # Rename module mrp_jit
    util.rename_module(cr, 'mrp_jit', 'procurement_jit')

    # Add stock_account moodule, automatically installed when stock and account are
    util.new_module(cr, 'stock_account', auto_install_deps=('stock', 'account'))

    # Sale stock should depend on stock_account
    util.new_module_dep(cr, 'sale_stock', 'stock_account')

    # Remove dependency of purchase from mrp
    util.remove_module_deps(cr, 'purchase', ('mrp',))

    util.new_module_dep(cr, 'crm', 'sales_team')
    util.new_module_dep(cr, 'sale', 'sales_team')

    cr.execute("update ir_model_data set module=%s where module=%s and model=%s",
               ('sales_team', 'crm', 'crm.case.section',))

    util.remove_record(cr, 'base.user_groups_view')
