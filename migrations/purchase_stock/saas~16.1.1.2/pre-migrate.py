from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.report", "avg_receipt_delay")
    util.create_m2m(
        cr,
        "stock_move_created_purchase_line_rel",
        "stock_move",
        "purchase_order_line",
        "move_id",
        "created_purchase_line_id",
    )
    cr.execute(
        """
        INSERT INTO stock_move_created_purchase_line_rel (move_id,created_purchase_line_id)
             SELECT id, created_purchase_line_id
               FROM stock_move
              WHERE created_purchase_line_id IS NOT NULL
    """
    )
    util.update_field_usage(cr, "stock.move", "created_purchase_line_id", "created_purchase_line_ids")
    util.remove_field(cr, "stock.move", "created_purchase_line_id")
