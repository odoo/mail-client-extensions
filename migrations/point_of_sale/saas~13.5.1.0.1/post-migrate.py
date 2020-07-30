# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT DISTINCT product_id
        FROM pos_order_line
    """
    )

    product_ids = [r[0] for r in cr.fetchall()]
    products = util.env(cr)["product.product"].browse(product_ids)
    product_names = [(p.display_name, p.id) for p in products]
    cr.executemany(
        """
        UPDATE pos_order_line pl
        SET full_product_name = %s
        WHERE product_id = %s
    """,
        product_names,
    )
