# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'hr.employee', 'account_id')

    util.create_column(cr, 'account_analytic_line', 'timesheet_invoice_type', 'varchar')
    cr.execute("""
        WITH so_line AS (
            SELECT L.id as id,  CASE T.invoice_policy
                                       WHEN 'order' THEN 'billable_fixed'
                                       WHEN 'delivery' THEN 'billable_time'
                                       ELSE 'non_billable'
                                END AS billable_type
            FROM sale_order_line L, product_product P, product_template T
            WHERE L.product_id = P.id AND P.product_tmpl_id = T.id AND T.type = 'service'
        )
        UPDATE account_analytic_line A
        SET timesheet_invoice_type = S.billable_type
        FROM so_line S
        WHERE S.id = A.so_line AND project_id IS NOT NULL
    """)

    util.create_column(cr, 'account_analytic_line', 'timesheet_invoice_id', 'int4')
    cr.execute("""
        UPDATE account_analytic_line A
        SET timesheet_invoice_id = ail.invoice_id
        FROM sale_order_line sol
        JOIN sale_order_line_invoice_rel so_invoice_line ON so_invoice_line.order_line_id = sol.id
        JOIN account_invoice_line ail ON so_invoice_line.invoice_line_id = ail.id
        WHERE A.project_id IS NOT NULL AND A.so_line = sol.id
    """)

    util.create_column(cr, 'account_analytic_line', 'timesheet_revenue', 'numeric')
