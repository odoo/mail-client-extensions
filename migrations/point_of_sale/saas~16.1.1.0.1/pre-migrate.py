from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "number_of_opened_session", "number_of_rescue_session")
    util.create_column(cr, "pos_order", "shipping_date", "date")
    query = """
        UPDATE pos_order
           SET shipping_date = stock_picking.scheduled_date
          FROM stock_picking
         WHERE pos_order.id = stock_picking.pos_order_id
           AND stock_picking.scheduled_date IS NOT null
           AND pos_order.to_ship = true
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="pos_order"))

    def adapter(leaf, _o, _n):
        _, op, right = leaf
        if op == "!=":
            right = not right
        new_op = "!=" if right else "="
        return [("shipping_date", new_op, False)]

    util.update_field_usage(cr, "pos.order", "to_ship", "shipping_date", domain_adapter=adapter)
    util.remove_field(cr, "pos.order", "to_ship")
