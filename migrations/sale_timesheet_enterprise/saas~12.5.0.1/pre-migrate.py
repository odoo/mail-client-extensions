# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.project", "allow_billable", "industry_fsm", "sale_timesheet_enterprise")
    util.move_field_to_module(cr, "project.task", "allow_billable", "industry_fsm", "sale_timesheet_enterprise")

    util.create_column(cr, "project_project", "allow_timesheet_timer", "boolean")
    util.create_column(cr, "project_project", "allow_billable", "boolean")
    cr.execute("UPDATE project_project SET allow_billable = TRUE WHERE billable_type != 'no'")
    util.create_column(cr, "project_task", "timesheet_timer_first_start", "timestamp without time zone")
    util.create_column(cr, "project_task", "timesheet_timer_last_stop", "timestamp without time zone")
    util.create_column(cr, "project_task", "allow_billable", "boolean")

    util.remove_field(cr, "res.company", "use_timesheet_timer")
    util.remove_field(cr, "res.config.settings", "use_timesheet_timer")
