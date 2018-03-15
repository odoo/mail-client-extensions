# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'hr.expense.sheet', 'responsible_id', 'user_id')
    util.remove_field(cr, 'res.config.settings', 'module_sale_management')

    util.rename_xmlid(cr, 'hr_expense.hr_expense_form_view', 'hr_expense.hr_expense_view_form')
    util.remove_record(cr, 'hr_expense.menu_hr_expense_sheet_all_all')

    util.remove_view(cr, 'hr_expense.report_expense')
    util.remove_record(cr, 'hr_expense.action_report_hr_expense')
