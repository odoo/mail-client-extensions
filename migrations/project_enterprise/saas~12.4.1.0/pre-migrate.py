# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "project.task.type", "is_closed", "helpdesk_timesheet", "project_enterprise")

    util.remove_record(cr, "project_enterprise.project_task_action_planning")
    util.remove_record(cr, "project_enterprise.project_task_menu_planning")
    util.remove_record(cr, "project_enterprise.project_task_menu")
