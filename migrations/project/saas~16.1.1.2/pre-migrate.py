# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.project_task_view_tree_activity")
    util.rename_xmlid(cr, "project.action_view_all_task", "project.action_view_my_task")
    util.rename_xmlid(cr, "project.open_view_all_task_list_kanban", "project.open_view_my_task_list_kanban")
    util.rename_xmlid(cr, "project.open_view_all_task_list_tree", "project.open_view_my_task_list_tree")
    util.rename_xmlid(cr, "project.open_view_all_task_list_calendar", "project.open_view_my_task_list_calendar")
