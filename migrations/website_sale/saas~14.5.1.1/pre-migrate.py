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

    util.create_column(cr, "product_product", "base_unit_count", "float", default=1)
    util.create_column(cr, "product_template", "base_unit_count", "float")
    util.explode_execute(
        cr,
        """
        WITH info AS (
            SELECT t.id
              FROM product_template t
              JOIN product_product p
                ON p.product_tmpl_id = t.id
             WHERE {parallel_filter}
             GROUP BY t.id
            HAVING COUNT(*) = 1
        ) UPDATE product_template t
             SET base_unit_count = 1
            FROM info
           WHERE info.id=t.id
        """,
        table="product_template",
        alias="t",
    )

    util.create_column(cr, "product_product", "base_unit_id", "int4")
    util.create_column(cr, "product_template", "base_unit_id", "int4")
