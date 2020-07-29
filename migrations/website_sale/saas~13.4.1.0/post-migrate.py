# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    promo_style_id = util.ref(cr, "website_sale.image_promo")
    sale_ribbon_id = util.ref(cr, "website_sale.sale_ribbon")
    cr.execute(
        """
        UPDATE product_template t
           SET website_ribbon_id = %s
          FROM product_style_product_template_rel r
         WHERE t.id=r.product_template_id
           AND r.product_style_id = %s
    """,
        (sale_ribbon_id, promo_style_id),
    )
    cr.execute(
        "SELECT 1 FROM product_style_product_template_rel WHERE product_style_id = %s LIMIT 1",
        [util.ref(cr, "website_sale.image_full")],
    )
    if cr.rowcount:
        cr.execute(
            "UPDATE ir_ui_view SET active = true WHERE id = %s", [util.ref(cr, "website_sale.products_images_full")]
        )

    util.remove_field(cr, "product.template", "website_style_ids")
    util.remove_field(cr, "product.product", "website_style_ids")
    cr.execute("DROP TABLE IF EXISTS product_style_product_template_rel")

    util.remove_model(cr, "product.style")
