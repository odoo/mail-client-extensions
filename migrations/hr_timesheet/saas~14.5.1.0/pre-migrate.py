# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr, "res.company", "leave_timesheet_project_id", "project_timesheet_holidays", "hr_timesheet"
    )
    util.rename_field(cr, "res.company", "leave_timesheet_project_id", "internal_project_id")
    util.create_column(cr, "res_company", "internal_project_id", "int4")
    util.remove_view(cr, "hr_timesheet.portal_subtask_timesheet_tables")

    util.delete_unused(cr, "hr_timesheet.hr_timesheet_config_settings_menu_action")

    if not util.module_installed(cr, "timesheet_grid"):
        util.remove_field(cr, "res.config.settings", "timesheet_min_duration")
        util.remove_field(cr, "res.config.settings", "timesheet_rounding")
        util.remove_record(cr, "hr_timesheet.ir_config_parameter_timesheet_rounding")
        util.remove_record(cr, "hr_timesheet.ir_config_parameter_timesheet_min_duration")
