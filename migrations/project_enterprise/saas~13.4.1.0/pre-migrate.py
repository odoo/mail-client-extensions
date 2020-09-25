# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "planned_date_begin_formatted")

    util.remove_view(cr, "project_enterprise.project_task_view_form")
    util.remove_view(cr, "project_enterprise.view_task_project_user_search_with_planned_dates")
