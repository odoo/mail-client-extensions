# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_sale_line_employee_map", "cost", "float8")
    util.create_column(cr, "project_sale_line_employee_map", "is_cost_changed", "boolean", default="False")
    util.rename_field(cr, "project.task", "analytic_account_id", "so_analytic_account_id")

    query = """
        UPDATE project_sale_line_employee_map map
           SET cost = emp.timesheet_cost
          FROM hr_employee emp
         WHERE emp.id = map.employee_id
    """
    util.parallel_execute(
        cr, util.explode_query_range(cr, query, table="project_sale_line_employee_map", prefix="map.")
    )
