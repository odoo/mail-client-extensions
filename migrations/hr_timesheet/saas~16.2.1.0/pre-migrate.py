# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_project_timesheet_synchro")
    util.remove_field(cr, "account.analytic.line", "ancestor_task_id")
    util.remove_field(cr, "timesheets.analysis.report", "ancestor_task_id")
    util.create_column(cr, "account_analytic_line", "parent_task_id", "int4")

    query = """
        UPDATE account_analytic_line l
           SET parent_task_id = t.parent_id
          FROM project_task t
         WHERE t.id = l.task_id
           AND t.parent_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="l"))
