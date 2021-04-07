# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_ui_view
           SET active = TRUE,
               customize_show = FALSE
         WHERE key = 'website_sale.ecom_show_extra_fields'
        """
    )

    util.create_column(cr, "website_snippet_filter", "product_cross_selling", "boolean", default=False)
    util.remove_record(cr, "website_sale.dynamic_snippet_products_action")
    util.remove_record(cr, "website_sale.dynamic_filter_demo_products")

    util.remove_view(cr, "website_sale.s_products_recently_viewed")
    util.remove_view(cr, "website_sale.recently_viewed_products_product")
    util.remove_view(cr, "website_sale.payment_sale_note")

    util.create_column(cr, "website", "cart_add_on_page", "boolean", default=True)
