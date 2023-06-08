# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "sale.temporal.recurrence", ["name"])
    util.explode_execute(
        cr,
        """
        UPDATE product_pricing pp
           SET currency_id = pl.currency_id
          FROM product_pricelist pl
         WHERE pp.pricelist_id = pl.id
           AND pp.currency_id IS NULL
        """,
        table="product_pricing",
        alias="pp",
    )
    util.explode_execute(
        cr,
        """
        UPDATE product_pricing pp
           SET currency_id = c.currency_id
          FROM product_template pt
          JOIN res_company c
            ON pt.company_id = c.id
         WHERE pp.pricelist_id IS NULL
           AND pp.currency_id IS NULL
           AND pp.product_template_id = pt.id
        """,
        table="product_pricing",
        alias="pp",
    )
