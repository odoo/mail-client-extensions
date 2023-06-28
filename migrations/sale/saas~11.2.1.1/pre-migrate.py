# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    byebye = util.splitlines("""
        mail_template_data_notification_email_sale_order
        filter_sale_report_sales_funnel
        filter_sale_report_salespersons
        filter_sale_report_salesteam
        filter_isale_report_product
    """)
    for record in byebye:
        util.remove_record(cr, 'sale.' + record)

    util.remove_field(cr, 'sale.order.line', 'qty_delivered_updateable')
    util.create_column(cr, 'sale_order_line', 'is_expense', 'boolean')
    util.create_column(cr, 'sale_order_line', 'qty_delivered_manual', 'numeric')
    util.create_column(cr, 'sale_order_line', 'qty_delivered_method', 'varchar')

    with_sale_stock = '' if util.module_installed(cr, 'sale_stock') else '--'
    with_sale_timesheet = '' if util.module_installed(cr, 'sale_timesheet') else '--'

    cr.execute("""
    WITH cte AS (
        SELECT l.id
          FROM sale_order_line l
          JOIN product_product p ON (p.id = l.product_id)
          JOIN product_template t ON (t.id = p.product_tmpl_id)
          JOIN account_analytic_line a ON (a.so_line = l.id)
         WHERE t.expense_policy!='no'
      GROUP BY l.id
    )
        UPDATE sale_order_line l
           SET is_expense = true
          FROM cte
         WHERE l.id = cte.id
    """)

    util.explode_execute(
        cr,
        """
        UPDATE sale_order_line l
           SET qty_delivered_manual = CASE WHEN l.is_expense THEN 0
                         {with_sale_stock} WHEN t.type IN ('consu', 'product') THEN 0
                     {with_sale_timesheet} WHEN t.type = 'service' AND t.service_type = 'timesheet' THEN 0
                                           ELSE qty_delivered
                                       END,
               qty_delivered_method = CASE WHEN l.is_expense THEN 'analytic'
                         {with_sale_stock} WHEN t.type IN ('consu', 'product') THEN 'stock_move'
                     {with_sale_timesheet} WHEN t.type = 'service' AND t.service_type = 'timesheet' THEN 'timesheet'
                                           ELSE 'manual'
                                       END
          FROM product_product p
          JOIN product_template t ON (t.id = p.product_tmpl_id)
         WHERE p.id = l.product_id
        """.format(**locals()),     # poor man's PEP498
        table="sale_order_line",
        alias="l",
    )
    # odoo/odoo@faf6165e037bcb1afee8a4881f3a166c86fdee59
    util.rename_field(cr, 'res.config.settings', 'default_deposit_product_id', 'deposit_default_product_id')
