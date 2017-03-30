# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'project.config.settings', 'timesheet_max_difference')
    util.remove_view(
        cr, 'hr_timesheet_attendance.view_config_settings_form_inherit_hr_timesheet_attendance')
