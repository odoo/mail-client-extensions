# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_sale.product_edit_options")
    util.remove_view(cr, "website_sale.search_count_box")
    util.remove_view(cr, "website_sale.user_navbar_inherit_website_sale")
    util.remove_view(cr, "website_sale.recommended_products")

    util.rename_xmlid(cr, "website_sale.product_picture_magnify_auto", "website_sale.product_picture_magnify_hover")
    util.rename_xmlid(cr, "website_sale.product_picture_magnify", "website_sale.product_picture_magnify_click")
