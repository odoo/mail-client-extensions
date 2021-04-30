# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "order_id", "int4")

    query = """
        UPDATE account_analytic_line l
           SET order_id = sol.order_id
          FROM sale_order_line sol
         WHERE sol.id = l.so_line
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", prefix="l."))

    if util.module_installed(cr, "industry_fsm_sale"):
        util.move_field_to_module(
            cr, "project.sale.line.employee.map", "timesheet_product_id", "sale_timesheet", "industry_fsm_sale"
        )
    else:
        util.remove_field(cr, "project.sale.line.employee.map", "timesheet_product_id")
