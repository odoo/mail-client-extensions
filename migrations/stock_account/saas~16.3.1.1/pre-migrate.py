# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_valuation_layer", "categ_id", "integer")
    util.explode_execute(
        cr,
        """
        UPDATE stock_valuation_layer svl
           SET categ_id = pt.categ_id
          FROM product_product pp
          JOIN product_template pt
            ON pp.product_tmpl_id = pt.id
         WHERE svl.product_id = pp.id
        """,
        table="stock_valuation_layer",
        alias="svl",
    )
