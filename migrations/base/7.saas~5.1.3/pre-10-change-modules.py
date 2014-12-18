# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module_dep(cr, 'resource', 'base')     # was depending on "process" only

    util.new_module_dep(cr, 'pad', 'web')
    util.remove_module_deps(cr, 'pad', ('base',))

    util.new_module_dep(cr, 'report', 'web')
    util.new_module_dep(cr, 'product', 'report')

    util.new_module_dep(cr, 'warning', 'sale_stock')
    util.remove_module_deps(cr, 'warning', ('sale',))

    util.rename_module(cr, 'mrp_jit', 'procurement_jit')

    util.new_module(cr, 'stock_account', auto_install_deps=('stock', 'account'))

    util.new_module_dep(cr, 'mrp', 'stock_account')
    util.remove_module_deps(cr, 'mrp', ('stock', 'purchase'))
    
    util.move_field_to_module(cr, 'product.template', 'produce_delay', 'product', 'mrp')

    util.new_module_dep(cr, 'purchase', 'stock_account')
    util.remove_module_deps(cr, 'purchase', ('stock', 'procurement'))

    # invert stock and procurement dependency
    util.remove_module_deps(cr, 'procurement', ('stock',))
    util.new_module_dep(cr, 'stock', 'procurement')

    util.new_module_dep(cr, 'stock', 'web_kanban_gauge')
    util.new_module_dep(cr, 'stock', 'web_kanban_sparkline')
    util.remove_module_deps(cr, 'stock', ('account',))

    util.new_module_dep(cr, 'sale_stock', 'stock_account')
    util.remove_module_deps(cr, 'sale_stock', ('stock', 'procurement'))

    # sales & crm
    util.new_module(cr, 'sales_team', auto_install_deps=('mail', 'web_kanban_sparkline'))
    util.remove_module_deps(cr, 'crm', ('web_kanban_sparkline',))
    util.new_module_dep(cr, 'crm', 'sales_team')

    util.new_module_dep(cr, 'sale', 'sales_team')
    util.new_module_dep(cr, 'sale', 'procurement')

    util.move_model(cr, 'crm.case.section', 'crm', 'sales_team', move_data=True)
    util.move_field_to_module(cr, 'res.partner', 'section_id', 'crm', 'sales_team')
    util.move_field_to_module(cr, 'res.users', 'default_section_id', 'sale_crm', 'sales_team')

    # just to be correct (I doubt anybody installed this module)
    util.new_module_dep(cr, 'web_tests', 'web')
    util.new_module_dep(cr, 'web_tests', 'web_kanban')

    # remove old modules
    util.remove_module(cr, 'process')
    util.remove_module(cr, 'audittrail')
    util.remove_module(cr, 'portal_project_long_term')
    util.remove_module(cr, 'project_long_term')
    util.remove_module(cr, 'product_manufacturer')
    util.remove_module(cr, 'project_gtd')
    util.remove_module(cr, 'stock_location')
    util.remove_module(cr, 'stock_no_auto_picking')
    util.remove_module(cr, 'web_hello')
    util.remove_module(cr, 'website_sale_crm')
    util.remove_module(cr, 'document_ftp')
