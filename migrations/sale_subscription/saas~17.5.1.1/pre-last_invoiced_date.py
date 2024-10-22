from odoo.upgrade import util


def migrate(cr, version):
    # Ensure existing in progress subscriptions are processed by the _cron_recurring_create_invoice
    # This ensure the previous behavior is kept
    util.explode_execute(
        cr,
        """
            UPDATE sale_order so
               SET require_payment=False
             WHERE subscription_state IN ('3_progress', '4_paused')
               AND payment_token_id is NULL
        """,
        table="sale_order",
        alias="so",
    )

    # fill the last_invoiced_date value based on last deferred_end_date of posted invoice
    util.create_column(cr, "sale_order_line", "last_invoiced_date", "date")
    query = """
        WITH _cte AS (
            SELECT r.order_line_id,
                   (
                      SELECT max(d)
                        FROM (
                            SELECT unnest(array_agg(ml.deferred_end_date) FILTER (WHERE m.move_type = 'out_invoice')) as d
                           EXCEPT
                            SELECT unnest(array_agg(ml.deferred_end_date) FILTER (WHERE m.move_type = 'out_refund')) as d
                       ) as _
                  ) as last_invoiced_date
              FROM sale_order_line_invoice_rel r
              JOIN sale_order_line ol       -- needed for explode
                ON ol.id = r.order_line_id
              JOIN account_move_line ml
                ON ml.id = r.invoice_line_id
              JOIN account_move m
                ON m.id = ml.move_id
             WHERE m.state = 'posted'
               AND m.move_type IN ('out_invoice', 'out_refund')
               AND ml.deferred_end_date IS NOT NULL
               AND {parallel_filter}
          GROUP BY r.order_line_id
        )
        UPDATE sale_order_line ol
           SET last_invoiced_date = _cte.last_invoiced_date
          FROM _cte
         WHERE _cte.order_line_id = ol.id
    """
    util.explode_execute(cr, query, table="sale_order_line", alias="ol")
