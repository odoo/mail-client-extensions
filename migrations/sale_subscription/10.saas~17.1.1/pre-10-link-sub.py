# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_order_line', 'subscription_id', 'int4')
    col = 'analytic_account_id' if util.version_gte('10.saas~18') else 'project_id'
    cr.execute("""
        WITH so_sub(so, sub) AS (
            SELECT o.id as so, s.id as sub
              FROM sale_order o
              JOIN sale_subscription s ON (o.{col} = s.analytic_account_id)
        ),
        recurring_products(id) AS (
            SELECT p.id
              FROM product_product p
              JOIN product_template t ON (t.id = p.product_tmpl_id)
             WHERE t.recurring_invoice = true
        )
        UPDATE sale_order_line l
           SET subscription_id = s.sub
          FROM so_sub s, recurring_products p
         WHERE s.so = l.order_id
           AND p.id = l.product_id
    """.format(col=col))

    util.create_column(cr, 'account_invoice_line', 'subscription_id', 'int4')
    cr.execute("""
        WITH recurring_products(id) AS (
            SELECT p.id
              FROM product_product p
              JOIN product_template t ON (t.id = p.product_tmpl_id)
             WHERE t.recurring_invoice = true
        )
        UPDATE account_invoice_line l
           SET subscription_id = s.id
          FROM sale_subscription s, recurring_products p
         WHERE s.analytic_account_id = l.account_analytic_id
           AND p.id = l.product_id
    """)
