# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'hr.attendance', 'sheet_id')
    util.remove_field(cr, 'hr.attendance', 'sheet_id_computed')
    util.remove_field(cr, 'res.company', 'timesheet_max_difference')

    util.remove_record(cr, 'hr_timesheet_attendance.access_hr_timesheet_sheet_sheet_day')
    util.remove_record(cr, 'hr_timesheet_attendance.access_hr_timesheet_sheet_sheet_day_user')
