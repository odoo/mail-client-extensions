# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.task", "overlap_warning")
    util.rename_xmlid(
        cr, "project_enterprise.open_view_all_task_list_gantt", "project_enterprise.open_view_my_task_list_gantt"
    )
