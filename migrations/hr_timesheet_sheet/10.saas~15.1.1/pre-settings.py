# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Note: field `module_project_timesheet_synchro` has been moved to module `project`
    util.remove_field(cr, 'project.config.settings', 'timesheet_range')
    util.remove_view(
        cr, 'hr_timesheet_sheet.view_config_settings_form_inherit_hr_timesheet_sheet')
