import logging

from odoo.upgrade import util

_logger = logging.getLogger(f"odoo.upgrade.sale.{__name__}")


def migrate(cr, version):
    query = """
        WITH no_posted_invoices AS (
            SELECT o.id
              FROM sale_order o
         LEFT JOIN sale_order_line ol
                ON ol.order_id = o.id
         LEFT JOIN sale_order_line_invoice_rel r
                ON r.order_line_id = ol.id
         LEFT JOIN account_move_line ml
                ON ml.id = r.invoice_line_id
         LEFT JOIN account_move m
                ON m.id = ml.move_id
               AND m.move_type IN ('out_invoice', 'out_refund')
               AND m.state = 'posted'
             WHERE m.id IS NULL
               AND {parallel_filter}
        )
        UPDATE sale_order o
           SET amount_to_invoice = o.amount_total
          FROM no_posted_invoices n
         WHERE n.id = o.id
    """
    _logger.info("Update orders without any posted invoices")
    util.explode_execute(cr, query, table="sale_order", alias="o")

    query = """
        WITH posted_invoices AS (
            SELECT DISTINCT o.id as order_id, m.id as move_id
              FROM sale_order o
              JOIN sale_order_line ol
                ON ol.order_id = o.id
              JOIN sale_order_line_invoice_rel r
                ON r.order_line_id = ol.id
              JOIN account_move_line ml
                ON ml.id = r.invoice_line_id
              JOIN account_move m
                ON m.id = ml.move_id
             WHERE m.move_type IN ('out_invoice', 'out_refund')
               AND m.state = 'posted'
               AND {parallel_filter}
        ),
        total_invoiced AS (
            SELECT r.order_id, SUM(m.amount_total) as amount_total
              FROM posted_invoices r
              JOIN sale_order o
                ON o.id = r.order_id
              JOIN account_move m
                ON m.id = r.move_id
          GROUP BY r.order_id, o.currency_id
            HAVING array_agg(DISTINCT m.currency_id) = ARRAY[o.currency_id]
        )
        UPDATE sale_order o
           SET amount_to_invoice = o.amount_total - t.amount_total
          FROM total_invoiced  t
         WHERE t.order_id = o.id
    """
    _logger.info("Update orders with all posted invoices in the same currency")
    util.explode_execute(cr, query, table="sale_order", alias="o")

    query = "SELECT id FROM sale_order WHERE amount_to_invoice IS NULL"
    util.recompute_fields(cr, "sale.order", ["amount_to_invoice"], query=query)
