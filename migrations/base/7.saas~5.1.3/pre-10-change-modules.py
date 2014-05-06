# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    #Remove process
    util.remove_module(cr, 'process')
    
    dependencies = ['account', 'crm', 'hr_expense', 'hr_holidays', 'hr', 'hr_timesheet', 'hr_timesheet_sheet', 
                                            'membership', 'mrp_operations', 'mrp', 'procurement', 'product', 'project', 'project_mrp',
                                            'project_timesheet', 'purchase',
                                            'sale', 'sale_crm', 'sale_stock', ]
    for depend in dependencies:
        util.remove_module_deps(cr, depend, ('process',))
    
    
    # Remove stock_location
    util.remove_module(cr, 'stock_location')
    
    # Inverse dependency of procurement from stock
    util.remove_module_deps(cr, 'procurement', ('stock',))
    util.new_module_dep(cr, 'stock', 'procurement')

    #Add dependencies from stock on web modules
    util.new_module_dep(cr, 'stock', 'web_kanban_gauge')
    util.new_module_dep(cr, 'stock', 'web_kanban_sparkline')
    # Rename module mrp_jit
    util.rename_module(cr, 'mrp_jit', 'procurement_jit')

    # Add stock_account moodule, automatically installed when stock and account are
    util.new_module(cr, 'stock_account', auto_install_deps=('stock', 'account'))
    
    
    #Sale stock should depend on stock_account
    util.new_module_dep(cr, 'sale_stock', 'stock_account')
    
    # Remove dependency of purchase from mrp
    util.remove_module_deps(cr, 'purchase', ('mrp',))