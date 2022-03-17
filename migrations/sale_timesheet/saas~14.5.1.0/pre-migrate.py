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
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="project_sale_line_employee_map", alias="map"))
    util.remove_view(cr, "sale_timesheet.project_profitability_timesheet_panel")
    util.remove_view(cr, "sale_timesheet.progressbar")
    util.remove_view(cr, "sale_timesheet.timesheet_plan")
    util.remove_record(cr, "sale_timesheet.project_timesheet_action_client_timesheet_plan")
    util.remove_record(cr, "sale_timesheet.project_profitability_report_action")
    util.remove_menus(cr, [util.ref(cr, "sale_timesheet.menu_project_profitability_analysis")])

    query = """
            WITH timesheets AS (
                SELECT aal.id,
                       aal.so_line,
                       pt.type AS product_type,
                       pt.invoice_policy,
                       pt.service_type
                  FROM account_analytic_line aal
             LEFT JOIN sale_order_line sol ON sol.id = aal.so_line
             LEFT JOIN product_product pro ON pro.id = sol.product_id
             LEFT JOIN product_template pt ON pt.id = pro.product_tmpl_id
                 WHERE {parallel_filter}
            )
            UPDATE account_analytic_line aal
                SET timesheet_invoice_type =
                    CASE
                        WHEN aal.project_id IS NOT NULL
                        THEN
                            CASE
                                WHEN aal.so_line IS NULL
                                THEN 'non_billable'
                                ELSE
                                    CASE
                                        WHEN t.product_type = 'service'
                                        THEN
                                            CASE
                                                WHEN t.invoice_policy = 'delivery'
                                                THEN
                                                    CASE
                                                        WHEN t.service_type = 'timesheet'
                                                        THEN
                                                            CASE
                                                                WHEN aal.amount > 0
                                                                THEN 'timesheet_revenues'
                                                                ELSE 'billable_time'
                                                            END
                                                        ELSE 'billable_fixed'
                                                    END
                                                WHEN t.invoice_policy = 'order'
                                                THEN 'billable_fixed'
                                                ELSE NULL
                                            END
                                        ELSE NULL
                                    END
                            END
                        ELSE
                            CASE
                                WHEN t.so_line IS NOT NULL
                                AND t.product_type = 'service'
                                THEN 'service_revenues'
                                WHEN aal.amount >= 0
                                THEN 'other_revenues'
                                ELSE 'other_costs'
                            END
                    END
                FROM timesheets t
             WHERE t.id = aal.id
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="aal"))
    util.remove_field(cr, "product.template", "service_upsell_warning")
