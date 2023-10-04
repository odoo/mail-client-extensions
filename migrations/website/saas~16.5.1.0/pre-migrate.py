# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE website_page
           SET url = '/no-url-migration-odoo-16.5.1', is_published = FALSE
         WHERE url IS NULL
        """
    )

    util.remove_view(cr, "website_sale_wishlist.template_header_magazine")
    util.remove_view(cr, "website_sale_wishlist.template_header_hamburger_full")
    util.remove_view(cr, "website_sale_wishlist.template_header_image")

    util.rename_xmlid(cr, "website_sale_wishlist.template_header_centered_logo", "website_sale_wishlist.template_header_search")
    util.rename_xmlid(cr, "website_sale_wishlist.template_header_slogan", "website_sale_wishlist.template_header_sales_two")
    util.rename_xmlid(cr, "website_sale_wishlist.template_header_contact", "website_sale_wishlist.template_header_sales_three")

    util.remove_view(cr, "website_sale.template_header_magazine")
    util.remove_view(cr, "website_sale.template_header_hamburger_full")
    util.remove_view(cr, "website_sale.template_header_image")

    util.rename_xmlid(cr, "website_sale.template_header_centered_logo", "website_sale.template_header_search")
    util.rename_xmlid(cr, "website_sale.template_header_slogan", "website_sale.template_header_sales_two")
    util.rename_xmlid(cr, "website_sale.template_header_contact", "website_sale.template_header_sales_three")

    util.remove_view(cr, "website.option_header_no_mobile_hamburger")
    util.remove_view(cr, "website.option_header_off_canvas_template_header_hamburger_full")
    util.remove_view(cr, "website.option_header_off_canvas_template_header_sidebar")
    util.remove_view(cr, "website.option_header_off_canvas_template_header_hamburger")
    util.remove_view(cr, "website.option_header_off_canvas_logo_show")
    util.remove_view(cr, "website.option_header_off_canvas")
    util.remove_view(cr, "website.template_header_magazine_oe_structure_header_magazine_1")
    util.remove_view(cr, "website.template_header_magazine")
    util.remove_view(cr, "website.template_header_hamburger_full_oe_structure_header_hamburger_full_1")
    util.remove_view(cr, "website.template_header_hamburger_full")
    util.remove_view(cr, "website.template_header_image_oe_structure_header_image_1")
    util.remove_view(cr, "website.template_header_image")
    util.remove_view(cr, "website.template_header_boxed_oe_structure_header_boxed_1")
    util.remove_view(cr, "website.template_header_contact_oe_structure_header_contact_1")
    util.remove_view(cr, "website.template_header_slogan_oe_structure_header_slogan_3")
    util.remove_view(cr, "website.template_header_slogan_oe_structure_header_slogan_1")
    util.remove_view(cr, "website.template_header_slogan_align_right")
    util.remove_view(cr, "website.template_header_slogan_align_center")
    util.remove_view(cr, "website.template_header_sidebar_oe_structure_header_sidebar_1")
    util.remove_view(cr, "website.template_header_vertical_oe_structure_header_vertical_3")
    util.remove_view(cr, "website.template_header_vertical_oe_structure_header_vertical_2")
    util.remove_view(cr, "website.template_header_vertical_oe_structure_header_vertical_1")
    util.remove_view(cr, "website.template_header_hamburger_oe_structure_header_hamburger_3")
    util.remove_view(cr, "website.template_header_hamburger_oe_structure_header_hamburger_2")
    util.remove_view(cr, "website.template_header_hamburger_align_center")

    util.rename_xmlid(cr, "website.template_header_centered_logo", "website.template_header_search")
    util.rename_xmlid(cr, "website.template_header_slogan", "website.template_header_sales_two")
    util.rename_xmlid(cr, "website.template_header_contact", "website.template_header_sales_three")

    util.remove_view(cr, "website.language_selector_add_language")
