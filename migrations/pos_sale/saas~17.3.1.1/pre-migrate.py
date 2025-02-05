from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_order_line", "qty_delivered", "float8", default=0)
    util.explode_execute(
        cr,
        """
        WITH lines AS (
            SELECT line.id as line_id, sum(move.quantity) as qty_delivered
              FROM pos_order_line line
              JOIN pos_order pos
                ON line.order_id = pos.id
              JOIN stock_picking pick
                ON pick.pos_order_id = pos.id
              JOIN stock_picking_type p_type
                ON pick.picking_type_id = p_type.id
              JOIN stock_move move
                ON move.picking_id = pick.id
             WHERE pick.state = 'done'
               AND p_type.code = 'outgoing'
               AND move.state = 'done'
               AND pos.state IN ('paid', 'done', 'invoiced')
               AND move.product_id = line.product_id
               AND {parallel_filter}
          GROUP BY line.id
        )
        UPDATE pos_order_line line
           SET qty_delivered = lines.qty_delivered
          FROM lines
         WHERE lines.line_id = line.id
        """,
        table="pos_order_line",
        alias="line",
    )
