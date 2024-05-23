from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "sale_order_line_stock_route_rel", "sale_order_line", "stock_route")
    cr.execute(
        """
            INSERT INTO sale_order_line_stock_route_rel (sale_order_line_id, stock_route_id)
                 SELECT id, route_id FROM sale_order_line WHERE route_id IS NOT NULL
        """
    )
    util.remove_field(cr, "sale.order.line", "route_id")
