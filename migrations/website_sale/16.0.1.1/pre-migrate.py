# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_edit_options")
    util.remove_view(cr, "website_sale.search_count_box")
    util.remove_view(cr, "website_sale.user_navbar_inherit_website_sale")
    util.remove_view(cr, "website_sale.recommended_products")
    util.remove_view(cr, "website_sale.sort")
    util.remove_view(cr, "website_sale.add_grid_or_list_option")
    util.remove_view(cr, "website_sale.products_categories")
    util.remove_view(cr, "website_sale.filter_products_price")

    util.rename_xmlid(cr, "website_sale.product_picture_magnify_auto", "website_sale.product_picture_magnify_hover")
    util.rename_xmlid(cr, "website_sale.product_picture_magnify", "website_sale.product_picture_magnify_click")

    # Rename publisher into restricted editor
    util.rename_xmlid(
        cr, "website_sale.access_product_image_publisher", "website_sale.access_product_image_restricted_editor"
    )
    util.rename_xmlid(
        cr, "website_sale.access_ecom_extra_fields_publisher", "website_sale.access_ecom_extra_fields_restricted_editor"
    )
    util.rename_field(
        cr,
        "res.company",
        "website_sale_onboarding_payment_acquirer_state",
        "website_sale_onboarding_payment_provider_state",
    )
    util.rename_xmlid(
        cr, "website_sale.menu_ecommerce_payment_acquirers", "website_sale.menu_ecommerce_payment_providers"
    )
