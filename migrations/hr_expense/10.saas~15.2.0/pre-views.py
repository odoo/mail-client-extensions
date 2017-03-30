# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'hr_expense.view_hr_expense_configuration',
                      'hr_expense.hr_expense_config_settings_view_form')
    util.force_noupdate(cr, 'hr_expense.hr_expense_config_settings_view_form', False)
