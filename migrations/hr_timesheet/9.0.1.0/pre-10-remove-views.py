#!/usr/bin/env python
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'hr_timesheet.account_analytic_account_timesheet_form')
    util.remove_view(cr, 'hr_timesheet.hr_timesheet_employee_extd_form')
