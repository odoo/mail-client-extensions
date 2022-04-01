# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "product.template",
        "service_policy",
        {
            "ordered_timesheet": "ordered_prepaid",
        },
    )
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_pivot")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_graph")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_tree")
    util.remove_view(cr, "sale_timesheet.project_profitability_report_view_search")
    util.remove_record(cr, "sale_timesheet.ir_filter_project_profitability_report_costs_and_revenues")
    util.remove_model(cr, "project.profitability.report")

    query = """
        WITH timesheets AS (
            SELECT aal.id,
                   pt.service_type
              FROM account_analytic_line aal
              JOIN sale_order_line sol ON sol.id = aal.so_line
              JOIN product_product pro ON pro.id = sol.product_id
              JOIN product_template pt ON pt.id = pro.product_tmpl_id
             WHERE aal.timesheet_invoice_type = 'billable_fixed'
               AND pt.service_type in ('milestones', 'manual')
               AND {parallel_filter}
        )
        UPDATE account_analytic_line
           SET timesheet_invoice_type = 'billable_' || t.service_type
          FROM timesheets t
         WHERE t.id = account_analytic_line.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="aal"))

    query = """
        UPDATE account_analytic_line
           SET timesheet_invoice_type = 'other_costs'
         WHERE timesheet_invoice_type = 'service_revenues'
           AND amount < 0
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line"))
