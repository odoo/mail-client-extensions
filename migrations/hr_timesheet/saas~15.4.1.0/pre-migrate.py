# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "ancestor_task_id", "int4")
    util.create_column(cr, "account_analytic_line", "manager_id", "int4")

    query = """
        UPDATE account_analytic_line l
           SET ancestor_task_id = t.ancestor_id
          FROM project_task t
         WHERE t.id = l.task_id
           AND t.ancestor_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="l"))

    query = """
        UPDATE account_analytic_line l
           SET manager_id = hr.parent_id
          FROM hr_employee hr
         WHERE hr.id = l.employee_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="l"))
