# -*- coding: utf-8 -*-
from psycopg2.extras import execute_values

from odoo.tools import float_round

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "product_packaging", "sales", "boolean", default=True)

    util.create_column(cr, "sale_order_line", "product_packaging_qty", "float8")

    if util.module_installed(cr, "sale_stock"):
        util.move_field_to_module(cr, "sale.order.line", "product_packaging", "sale_stock", "sale")
        util.rename_field(cr, "sale.order.line", "product_packaging", "product_packaging_id")

        # compute `product_packaging_qty` column
        UoM = util.env(cr)["uom.uom"].browse

        cr.execute(
            """
                SELECT l.id, l.product_uom_qty, l.product_uom, pa.qty, pt.uom_id
                  FROM sale_order_line l
                  JOIN product_packaging pa ON pa.id = l.product_packaging_id
                  JOIN product_product pr ON pr.id = pa.product_id
                  JOIN product_template pt ON pt.id = pr.product_tmpl_id
            """
        )
        values = []
        for l_id, l_qty, l_uom, p_qty, p_uom in cr.fetchall():
            l_uom = UoM(l_uom)
            p_uom = UoM(p_uom)
            qty = float_round(l_uom._compute_quantity(l_qty, p_uom) / p_qty, p_uom.rounding)
            values.append((l_id, qty))

        execute_values(
            cr._obj,
            """
                UPDATE sale_order_line l
                   SET product_packaging_qty = v.qty
                  FROM (VALUES %s) AS v(id, qty)
                 WHERE l.id = v.id
            """,
            values,
        )

    else:
        util.create_column(cr, "sale_order_line", "product_packaging_id", "int4")

    util.convert_field_to_html(cr, "sale.order", "note")
