# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'base.config.settings', 'group_attendance_use_pin')
    util.force_noupdate(cr, 'hr_attendance.group_hr_attendance', False)

    util.remove_view(cr, 'hr_attendance.hr_attendance_view_config')
    util.force_noupdate(cr, 'hr_attendance.action_hr_attendance_settings', False)
