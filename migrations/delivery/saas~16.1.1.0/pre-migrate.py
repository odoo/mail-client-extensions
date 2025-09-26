from odoo.upgrade import util


def compute_shipping_weight(cr):
    util.create_column(cr, "sale_order", "shipping_weight", "float8")
    query = """
        WITH so AS (
            SELECT o.id,
                   SUM (CASE WHEN l.product_uom = t.uom_id
                        THEN l.product_uom_qty
                        ELSE round(l.product_uom_qty / ul.factor * ut.factor, ceil(-log(ut.rounding))::integer)
                    END * p.weight) AS w
              FROM sale_order_line l
              JOIN sale_order o
                ON o.id = l.order_id
              JOIN product_product p
                ON p.id = l.product_id
              JOIN product_template t
                ON t.id = p.product_tmpl_id
              JOIN uom_uom ul
                ON ul.id = l.product_uom
              JOIN uom_uom ut
                ON ut.id = t.uom_id
             WHERE t.type IN ('product', 'consu')
               AND l.is_delivery IS NOT TRUE
               AND l.display_type IS NULL
               AND l.product_uom_qty > 0
               AND {parallel_filter}
          GROUP BY o.id
        )
        UPDATE sale_order o
           SET shipping_weight = so.w
          FROM so
         WHERE so.id = o.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sale_order", alias="o"))


def migrate(cr, version):
    util.create_column(cr, "stock_move_line", "carrier_id", "int4")
    query = """
        UPDATE stock_move_line sml
           SET carrier_id = sp.carrier_id
          FROM stock_picking sp
         WHERE sml.picking_id = sp.id
           AND sp.carrier_id IS NOT NULL
    """
    util.explode_execute(cr, query, table="stock_move_line", alias="sml")
    util.update_field_usage(cr, "stock.move.line", "carrier_name", "carrier_id")

    util.remove_field(cr, "stock.move.line", "carrier_name")

    compute_shipping_weight(cr)
