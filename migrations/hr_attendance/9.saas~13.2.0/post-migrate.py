# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.split_group(cr, ['hr.group_hr_attendance', 'hr.group_hr_user'],
                     'hr_attendance.group_hr_attendance_user')
    util.split_group(cr, ['hr.group_hr_attendance', 'hr.group_hr_manager'],
                     'hr_attendance.group_hr_attendance_manager')
