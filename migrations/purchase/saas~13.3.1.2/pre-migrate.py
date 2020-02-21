# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order_line", "qty_to_invoice", "numeric")

    cr.execute(
        """
        WITH pol_po_p AS (
            SELECT pol.id,
                CASE 
                    WHEN po.state in ('purchase', 'done') AND pt.purchase_method = 'purchase' THEN pol.product_uom_qty - pol.qty_invoiced
                    WHEN po.state in ('purchase', 'done') AND pt.purchase_method != 'purchase' THEN pol.qty_received - pol.qty_invoiced
                    ELSE 0.0
                END AS qty_to_invoice
            FROM purchase_order_line pol
            JOIN product_product p ON pol.product_id = p.id
            JOIN product_template pt ON p.product_tmpl_id = pt.id
            JOIN purchase_order po ON pol.order_id = po.id
        )
        UPDATE purchase_order_line pol 
           SET qty_to_invoice = p.qty_to_invoice
          FROM pol_po_p p
         WHERE pol.id = p.id
        """
    )

    cr.execute(
        """
        WITH pol AS (
          SELECT order_id,
                 bool_or(qty_to_invoice != 0) as or_cond,
                 bool_and(qty_to_invoice = 0) as and_cond
            FROM purchase_order_line
        GROUP BY order_id
        ),
        pol_po AS (
        SELECT po.id, 
            CASE 
                WHEN po.state NOT IN ('purchase', 'done') THEN 'no'
                WHEN pol.or_cond THEN 'to invoice'
                WHEN pol.and_cond THEN 'invoiced'
                ELSE 'no'
            END AS invoice_status
          FROM purchase_order po
          JOIN pol ON pol.order_id = po.id
        )
        UPDATE purchase_order po 
           SET invoice_status = p.invoice_status 
          FROM pol_po p
         WHERE po.id = p.id
        """
    )