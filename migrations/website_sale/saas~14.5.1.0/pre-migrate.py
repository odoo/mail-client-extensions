# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_sale.s_products_searchbar_000_js")
    util.remove_view(cr, "website_sale.searchbar_input_snippet_options")
    util.remove_view(cr, "website_sale.s_products_searchbar")
    util.remove_view(cr, "website_sale.s_products_searchbar_input")
    util.remove_view(cr, "website_sale.website_sale_products_search_box")

    util.remove_view(cr, "website_sale.template_header_minimalist")
    util.remove_view(cr, "website_sale.product_template_form_view_invoice_policy")
