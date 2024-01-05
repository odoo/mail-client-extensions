# -*- coding: utf-8 -*-

from lxml import etree

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

    util.rename_xmlid(
        cr, "website_sale_wishlist.template_header_centered_logo", "website_sale_wishlist.template_header_search"
    )
    util.rename_xmlid(
        cr, "website_sale_wishlist.template_header_slogan", "website_sale_wishlist.template_header_sales_two"
    )
    util.rename_xmlid(
        cr, "website_sale_wishlist.template_header_contact", "website_sale_wishlist.template_header_sales_three"
    )

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

    cr.execute(
        """
        SELECT id,
               active
          FROM ir_ui_view
         WHERE key = 'website.header_call_to_action'
           AND website_id IS NOT NULL
        """
    )
    for view_id, active in cr.fetchall():
        with util.edit_view(cr, view_id=view_id, active=active) as arch:
            section = arch.find('.//section[@data-snippet="s_text_block"]')
            if section is None:
                section = """
                    <section class="oe_unremovable oe_unmovable s_text_block" data-snippet="s_text_block" data-name="Text">
                        <div class="container">
                            <a href="/contactus" class="oe_unremovable btn btn-primary btn_cta">Contact Us</a>
                        </div>
                    </section>
                    """
                div = arch.xpath('.//div[hasclass("oe_structure") and hasclass("oe_structure_solo")]')
                if div:
                    div[0].append(etree.fromstring(section))
                continue

            section_classes = section.attrib["class"].split(" ")
            new_classes = [cl for cl in ["oe_unremovable", "oe_unmovable"] if cl not in section_classes]
            if new_classes:
                section.attrib["class"] += " " + " ".join(new_classes)

            node = arch.xpath(".//a[hasclass('btn_cta') or hasclass('_cta')]")
            if not node:
                div = section.xpath('.//div[hasclass("container")]')
                if div:
                    div[0].append(
                        etree.fromstring(
                            """<a href="/contactus" class="oe_unremovable btn btn-primary btn_cta">Contact Us</a>"""
                        )
                    )
                continue
            a_classes = node[0].attrib["class"].split(" ")
            new_classes = [cl for cl in ["oe_unremovable", "btn_ca"] if cl not in a_classes]
            if new_classes:
                node[0].attrib["class"] += " " + " ".join(new_classes)
