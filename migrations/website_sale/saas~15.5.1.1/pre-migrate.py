# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_edit_options")
    util.remove_view(cr, "website_sale.search_count_box")
    util.remove_view(cr, "website_sale.user_navbar_inherit_website_sale")
    util.remove_view(cr, "website_sale.recommended_products")

    util.rename_xmlid(cr, "website_sale.product_picture_magnify_auto", "website_sale.product_picture_magnify_hover")
    util.rename_xmlid(cr, "website_sale.product_picture_magnify", "website_sale.product_picture_magnify_click")

    # Rename publisher into restricted editor
    util.rename_xmlid(
        cr, "website_sale.access_product_image_publisher", "website_sale.access_product_image_restricted_editor"
    )
    util.rename_xmlid(
        cr, "website_sale.access_ecom_extra_fields_publisher", "website_sale.access_ecom_extra_fields_restricted_editor"
    )
