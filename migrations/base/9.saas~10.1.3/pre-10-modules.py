# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.merge_module(cr, 'account_extra_reports', 'account')

    util.remove_view(cr, 'account_full_reconcile.view_move_line_form')
    util.merge_module(cr, 'account_full_reconcile', 'account')

    util.remove_view(cr, 'project_timesheet.view_account_analytic_line_tree_inherit_account_id')
    util.merge_module(cr, 'project_timesheet', 'hr_timesheet')

    util.remove_module_deps(cr, 'hr_timesheet', ('base', 'hr_attendance'))
    util.new_module_dep(cr, 'hr_timesheet', 'project')
    util.new_module_dep(cr, 'hr_timesheet_sheet', 'hr_attendance')

    util.new_module(cr, 'pos_data_drinks')
    util.new_module_dep(cr, 'pos_data_drinks', 'point_of_sale')

    util.remove_module_deps(cr, 'sale_service', ('project', 'sale'))
    util.new_module_dep(cr, 'website_sale_delivery', 'website_sale_stock')

    util.remove_module(cr, 'claim_from_delivery')
    util.remove_module(cr, 'web_view_editor')
    util.remove_module(cr, 'website_crm_claim')
