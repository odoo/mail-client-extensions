# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT product_id FROM pos_order_line WHERE product_id IS NOT NULL GROUP BY product_id")

    ids = [r[0] for r in cr.fetchall()]
    util.parallel_execute(
        cr,
        [
            cr.mogrify("UPDATE pos_order_line SET full_product_name = %s WHERE product_id = %s", [p.display_name, p.id])
            for p in util.iter_browse(util.env(cr)["product.product"], ids)
        ],
    )
