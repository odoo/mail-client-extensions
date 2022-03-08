# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    product_dynamic_snippets = [
        "dynamic_filter_template_product_product_add_to_cart",
        "dynamic_filter_template_product_product_view_detail",
        "dynamic_filter_template_product_product_mini_image",
        "dynamic_filter_template_product_product_mini_price",
        "dynamic_filter_template_product_product_mini_name",
        "dynamic_filter_template_product_product_centered",
        "dynamic_filter_template_product_product_borderless_1",
        "dynamic_filter_template_product_product_borderless_2",
        "dynamic_filter_template_product_product_banner",
        "dynamic_filter_template_product_product_horizontal_card",
        "price_dynamic_filter_template_product_product",
    ]
    for snippet in product_dynamic_snippets:
        util.force_noupdate(cr, f"website_sale.{snippet}", noupdate=False)

    util.force_noupdate(cr, "website_sale.s_dynamic_snippet_products_000_scss", noupdate=False)

    if util.module_installed(cr, "website_sale_stock"):
        util.rename_field(cr, "sale.order", "warning_stock", "shop_warning")
        util.move_field_to_module(cr, "sale.order", "shop_warning", "website_sale_stock", "website_sale")
        util.rename_field(cr, "sale.order.line", "warning_stock", "shop_warning")
        util.move_field_to_module(cr, "sale.order.line", "shop_warning", "website_sale_stock", "website_sale")
    else:
        util.create_column(cr, "sale_order", "shop_warning", "varchar")
        util.create_column(cr, "sale_order_line", "shop_warning", "varchar")
