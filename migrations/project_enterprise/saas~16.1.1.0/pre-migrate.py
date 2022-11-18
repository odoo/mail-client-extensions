# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_enterprise.report_project_task_user_view_search_inherited")
    util.remove_view(cr, "project_enterprise.view_task_search_form_inherit_enterprise")
    util.remove_field(cr, "report.project.task.user", "planning_overlap")
    util.remove_field(cr, "project.task", "overlap_warning")
    util.rename_xmlid(
        cr, "project_enterprise.open_view_all_task_list_gantt", "project_enterprise.open_view_my_task_list_gantt"
    )
