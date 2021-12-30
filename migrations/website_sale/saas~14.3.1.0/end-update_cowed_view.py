# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website_sale.product'
               AND website_id IS NOT NULL
               AND arch_db !~ '\yadd_to_cart_wrap\y'
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            div, div2 = util.lxml.etree.Element("div"), util.lxml.etree.Element("div")
            div.attrib.update({"id": "add_to_cart_wrap", "class": "d-inline"})
            div.extend(arch.xpath("//div[@class='js_product js_main_product']/a[@id='add_to_cart']"))
            div.extend(arch.xpath("//div[@class='js_product js_main_product']/div[@id='product_option_block']"))
            for node in arch.xpath("//div[@class='js_product js_main_product']"):
                node.append(div)
            div2.attrib.update({"id": "o_product_terms_and_share"})
            for node in arch.xpath("//div[@id='product_attributes_simple']"):
                node.append(div2)

    cr.execute(
        r"""
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website_sale.shop_product_carousel'
               AND website_id IS NOT NULL
               AND arch_db !~ '\yo_carousel_product_outer\y'
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view) as arch:
            for node in arch.xpath("//div[@id='o-carousel-product']/div[hasclass('carousel-outer')]"):
                node.attrib["class"] = "o_carousel_product_outer carousel-outer position-relative flex-grow-1"
