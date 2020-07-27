# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "timesheet_timer_first_start")
    util.remove_field(cr, "project.task", "timesheet_timer_last_stop")

    views = """
        project_view_form_inherit
        project_project_view_form_simplified_inherit

        project_task_view_form
        project_task_view_kanban

    """

    if not util.module_installed(cr, "timesheet_grid"):
        util.remove_field(cr, "project.project", "allow_timesheet_timer")
        cr.execute("ALTER TABLE project_project DROP CONSTRAINT IF EXISTS project_project_timer_only_when_timesheet")

        util.remove_field(cr, "project.task", "display_timesheet_timer")
        util.remove_field(cr, "project.task", "display_timer_start_secondary")
        util.remove_inherit_from_model(cr, "project.task", "timer.mixin")

        util.remove_field(cr, "account.analytic.line", "display_timer")
        util.remove_inherit_from_model(cr, "account.analytic.line", "timer.mixin")

        for view in util.splitlines(views):
            util.remove_view(cr, f"hr_timesheet.{view}")
    else:
        util.move_field_to_module(cr, "project.project", "allow_timesheet_timer", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "project.task", "display_timesheet_timer", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "project.task", "display_timer_start_secondary", "hr_timesheet", "timesheet_grid")
        util.move_field_to_module(cr, "account.analytic.line", "display_timer", "hr_timesheet", "timesheet_grid")

        for view in util.splitlines(views):
            util.rename_xmlid(cr, f"hr_timesheet.{view}", f"timesheet_grid.{view}")
