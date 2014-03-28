# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields now have foreign keys...
    util.ensure_m2o_func_field_data(cr, 'hr_analytic_timesheet', 'sheet_id', 'hr_timesheet_sheet_sheet')
