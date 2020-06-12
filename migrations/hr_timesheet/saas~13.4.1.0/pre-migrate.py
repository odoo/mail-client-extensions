# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "timesheet_timer_first_start")
    util.remove_field(cr, "project.task", "timesheet_timer_last_stop")

    if not util.has_enterprise():
        util.remove_field(cr, "project.project", "allow_timesheet_timer")
        util.remove_field(cr, "project.task", "display_timesheet_timer")
        util.remove_field(cr, "project.task", "display_timer_start_secondary")
        util.remove_field(cr, "account.analytic.line", "display_timer")
        util.remove_field(cr, "account.analytic.line", "user_timer_id")
        util.remove_field(cr, "project.task", "user_timer_id")
        util.remove_inherit_from_model(cr, "account.analytic.line", "timer.mixin")
        util.remove_inherit_from_model(cr, "project.task", "timer.mixin")
        cr.execute("ALTER TABLE project_project DROP CONSTRAINT IF EXISTS timer_only_when_timesheet")
    else:
        util.move_field_to_module(cr, "project.project", "allow_timesheet_timer", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "project.task", "display_timesheet_timer", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "project.task", "display_timer_start_secondary", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "account.analytic.line", "display_timer", "hr_timesheet", "timesheet_grid")
        util.rename_xmlid(cr, "hr_timesheet.project_view_form_inherit", "timesheet_grid.project_view_form_inherit")
        util.rename_xmlid(
            cr,
            "hr_timesheet.project_project_view_form_simplified_inherit",
            "timesheet_grid.project_project_view_form_simplified_inherit",
        )
        util.rename_xmlid(cr, "hr_timesheet.project_task_view_form", "timesheet_grid.project_task_view_form")
        util.rename_xmlid(cr, "hr_timesheet.project_task_view_kanban", "timesheet_grid.project_task_view_kanban")
