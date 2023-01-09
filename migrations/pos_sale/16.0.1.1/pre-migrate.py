# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "amount_unpaid", "numeric")
    query = """
        WITH _sale_orders AS (
            SELECT id
              FROM sale_order
             WHERE {parallel_filter}

        ), total_invoice_paid AS (
            SELECT ol.order_id, SUM(ml.price_total) as total_invoice_paid
              FROM sale_order_line ol
              JOIN _sale_orders o
                ON o.id = ol.order_id
              JOIN sale_order_line_invoice_rel m2m
                ON m2m.order_line_id = ol.id
              JOIN account_move_line ml
                ON ml.id = m2m.invoice_line_id
             WHERE ol.display_type IS NULL
               AND ml.parent_state != 'cancel'
          GROUP BY ol.order_id
        ),
        total_pos_paid AS (
            SELECT ol.order_id, SUM(pl.price_subtotal_incl) as total_pos_paid
              FROM sale_order_line ol
              JOIN _sale_orders o
                ON o.id = ol.order_id
              JOIN pos_order_line pl
                ON pl.sale_order_origin_id = ol.order_id
             WHERE ol.display_type IS NULL
          GROUP BY ol.order_id
        )

        UPDATE sale_order so
           SET amount_unpaid = so.amount_total - (COALESCE(tip.total_invoice_paid, 0) + COALESCE(tpp.total_pos_paid, 0))
          FROM _sale_orders me
     LEFT JOIN total_invoice_paid tip
            ON tip.order_id = me.id
     LEFT JOIN total_pos_paid tpp
            ON tpp.order_id = me.id
         WHERE me.id = so.id
    """

    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order"))
