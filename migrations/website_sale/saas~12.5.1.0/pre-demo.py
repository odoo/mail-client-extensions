# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_sale.product_template_attribute_line_1",
        "website_sale.product_1_attribute_3_product_template_attribute_line",
    )
    util.rename_xmlid(
        cr, "website_sale.product_template_attribute_value_1", "website_sale.product_1_attribute_3_value_2"
    )

    p1 = util.ref(cr, "website_sale.product_product_1")
    if p1:
        cr.execute(
            """
            INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
                 SELECT 'website_sale', 'product_product_1b', 'product.product', id, true
                   FROM product_product
                  WHERE product_tmpl_id = (SELECT product_tmpl_id FROM product_product WHERE id = %s)
                    AND id != %s
            """,
            [p1, p1],
        )
