# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "allow_timesheet_timer")
    util.remove_view(cr, "timesheet_grid.project_view_form_inherit")
    util.remove_view(cr, "timesheet_grid.project_project_view_form_simplified_inherit")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_timesheet,timesheet_grid}.ir_config_parameter_timesheet_rounding"))
    util.rename_xmlid(cr, *eb("{hr_timesheet,timesheet_grid}.ir_config_parameter_timesheet_min_duration"))

    util.move_field_to_module(cr, "res.config.settings", "timesheet_min_duration", "hr_timesheet", "timesheet_grid")
    util.move_field_to_module(cr, "res.config.settings", "timesheet_rounding", "hr_timesheet", "timesheet_grid")

    cr.execute(
        """
        UPDATE ir_config_parameter
           SET key='timesheet_grid.timesheet_min_duration'
         WHERE key='hr_timesheet.timesheet_min_duration'
    """
    )

    cr.execute(
        """
        UPDATE ir_config_parameter
           SET key='timesheet_grid.timesheet_rounding'
         WHERE key='hr_timesheet.timesheet_rounding'
     """
    )
