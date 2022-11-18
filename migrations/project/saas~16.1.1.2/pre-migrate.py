# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.project_task_view_tree_activity")
    util.rename_xmlid(cr, "project.action_view_all_task", "project.action_view_my_task")
    util.rename_xmlid(cr, "project.open_view_all_task_list_kanban", "project.open_view_my_task_list_kanban")
    util.rename_xmlid(cr, "project.open_view_all_task_list_tree", "project.open_view_my_task_list_tree")
    util.rename_xmlid(cr, "project.open_view_all_task_list_calendar", "project.open_view_my_task_list_calendar")
    util.remove_view(cr, "project.view_task_search_form_extended")
    util.remove_field(cr, "report.project.task.user", "ancestor_id")
    util.remove_field(cr, "report.project.task.user", "milestone_reached")
    util.remove_field(cr, "report.project.task.user", "milestone_deadline")
    util.rename_field(cr, "report.project.task.user", "state", "kanban_state")
