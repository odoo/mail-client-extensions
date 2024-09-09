from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "delivery_status", "varchar")
    cr.execute(
        """
        WITH states AS (
            SELECT sale_id AS order_id,
                   array_agg(state) as states
              FROM stock_picking
          GROUP BY 1
        )
        UPDATE sale_order so
           SET delivery_status='full'
          FROM states s
         WHERE s.order_id=so.id
           AND ARRAY['done', 'cancel']::varchar[] @> s.states
           AND array_position(s.states, 'done') > 0
    """
    )
    cr.execute(
        """
        WITH lines AS (
            SELECT distinct order_id
              FROM sale_order_line
             WHERE qty_delivered > 0
        ),
        picks AS (
            SELECT distinct sale_id AS order_id
              FROM stock_picking
        )
        UPDATE sale_order so
           SET delivery_status='partial'
          FROM lines l, picks p
         WHERE so.id=l.order_id
           AND so.id=p.order_id
           AND so.delivery_status IS NULL
    """
    )
    cr.execute(
        """
        WITH picks AS (
            SELECT distinct sale_id AS order_id
              FROM stock_picking
             WHERE state='done'
        )
        UPDATE sale_order so
           SET delivery_status='started'
          FROM picks p
         WHERE so.id=p.order_id
           AND so.delivery_status IS NULL
    """
    )
    cr.execute(
        """
        WITH not_cancelled AS (
             SELECT sale_id AS order_id
               FROM stock_picking sp
              WHERE sp.state != 'cancel'
              GROUP BY sp.sale_id
             HAVING COUNT(*) > 0
        )
        UPDATE sale_order so
           SET delivery_status='pending'
          FROM not_cancelled c
         WHERE c.order_id=so.id
           AND so.delivery_status IS NULL
    """
    )
