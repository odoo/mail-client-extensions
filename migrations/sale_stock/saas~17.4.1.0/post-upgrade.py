from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE sale_order_line l
           SET warehouse_id = o.warehouse_id
          FROM sale_order o
         WHERE o.id = l.order_id
           AND l.route_id IS NULL
    """
    util.explode_execute(cr, query, table="sale_order_line", alias="l")

    cr.execute("SELECT id FROM sale_order_line WHERE route_id IS NOT NULL")
    ids = [lid for (lid,) in cr.fetchall()]
    if ids:
        util.recompute_fields(cr, "sale.order.line", ["warehouse_id"], ids=ids)
