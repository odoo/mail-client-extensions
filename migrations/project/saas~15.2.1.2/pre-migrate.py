# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_m2m(
        cr,
        "account_analytic_tag_project_project_rel",
        "account_analytic_tag",
        "project_project",
        "account_analytic_tag_id",
        "project_project_id",
    )
    util.remove_record(cr, "project.menu_projects_group_stage")
    util.remove_record(cr, "project.open_view_project_all_group_stage")
    util.create_column(cr, "project_task", "is_closed", "boolean", default=False)
    query = """
        UPDATE project_task t
           SET is_closed = s.fold
          FROM project_task_type s
         WHERE s.id = t.stage_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="project_task", prefix="t."))
