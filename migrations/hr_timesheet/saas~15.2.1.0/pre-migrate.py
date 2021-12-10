# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.module_installed(cr, "timesheet_grid"):
        util.move_model(cr, "project.task.create.timesheet", "hr_timesheet", "timesheet_grid")
        util.rename_xmlid(cr, *eb("{hr_timesheet,timesheet_grid}.project_task_create_timesheet_view_form"))
        util.rename_xmlid(cr, *eb("{hr_timesheet,timesheet_grid}.access_project_task_create_timesheet"))
    else:
        util.remove_model(cr, "project.task.create.timesheet")
        util.remove_view(cr, "hr_timesheet.project_task_create_timesheet_view_form")
        util.remove_record(cr, "hr_timesheet.access_project_task_create_timesheet")
