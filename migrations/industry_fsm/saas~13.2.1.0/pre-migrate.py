# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.create_column(cr, "project_project", "allow_timesheets", "boolean"):
        cr.execute("UPDATE project_project SET allow_timesheets = not is_fsm")

    if util.create_column(cr, "project_project", "allow_timesheet_timer", "boolean"):
        cr.execute("UPDATE project_project SET allow_timesheet_timer = not is_fsm")
