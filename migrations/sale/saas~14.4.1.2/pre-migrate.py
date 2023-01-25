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
                SELECT l.id, l.product_uom_qty, l.product_uom, pa.qty, pt.uom_id, l.product_id=pa.product_id
                  FROM sale_order_line l
                  JOIN product_packaging pa ON pa.id = l.product_packaging_id
                  JOIN product_product pr ON pr.id = pa.product_id
                  JOIN product_template pt ON pt.id = pr.product_tmpl_id
            """
        )
        values = []
        bad_lines = []
        for l_id, l_qty, l_uom, p_qty, p_uom, same_product in cr.fetchall():
            l_uom = UoM(l_uom)
            p_uom = UoM(p_uom)
            if not same_product and l_uom.category_id != p_uom.category_id:
                bad_lines.append(l_id)
                continue
            qty = float_round(l_uom._compute_quantity(l_qty, p_uom) / p_qty, precision_rounding=p_uom.rounding)
            values.append((l_id, qty))

        if bad_lines:
            cr.execute(
                """
                SELECT l.id,
                       l.order_id,
                       l.product_id,
                       p.product_id
                  FROM sale_order_line l
                  JOIN product_packaging p
                    ON l.product_packaging_id = p.id
                 WHERE l.id IN %s
                 ORDER BY l.order_id, l.id
                """,
                [tuple(bad_lines)],
            )
            msg = util.dedent(
                """
                There is a mismatch on the UoM category of the products in some Sales Order Lines and their
                associated packaging. In order to continue the upgrade you must either set the same product
                on the line and the packaging, or change one of the UoM categories of the associated products.
                The faulty Sale Order Lines are:
                """
            )
            msg += "\n".join(
                f"  * line (id={lid},order={oid}) with product(id={lpid}), packaging has product(id={ppid})"
                for lid, oid, lpid, ppid in cr.fetchall()
            )
            raise util.MigrationError(f"\n{msg}\n")

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
