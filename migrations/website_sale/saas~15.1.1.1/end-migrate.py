# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    jsonb_column = util.column_type(cr, "ir_ui_view", "arch_db") == "jsonb"
    arch_db_column = "arch_db->>'en_US'" if jsonb_column else "arch_db"
    cr.execute(
        rf"""
            SELECT id
              FROM ir_ui_view
             WHERE key = 'website_sale.product'
               AND website_id IS NOT NULL
               AND {arch_db_column} !~ '\yo_wsale_cta_wrapper\y'
        """
    )
    for (view,) in cr.fetchall():
        with util.edit_view(cr, view_id=view, active=None) as arch:
            div_1 = util.lxml.etree.Element(
                "div", {"id": "o_wsale_cta_wrapper", "class": "d-inline-flex align-items-center mb-2 mr-auto"}
            )
            t_1 = util.lxml.etree.Element("t", {"t-set": "hasQuantities", "t-value": "false"})
            t_2 = util.lxml.etree.Element("t", {"t-set": "hasBuyNow", "t-value": "false"})
            t_3 = util.lxml.etree.Element("t", {"t-set": "ctaSizeBig", "t-value": "not hasQuantities or not hasBuyNow"})
            div_1.extend([t_1, t_2, t_3])
            div_1.extend(arch.xpath("//div[@id='add_to_cart_wrap']"))
            div_1.extend(arch.xpath("//div[@id='product_option_block']"))
            for node in arch.xpath("//div[hasclass('js_main_product')]"):
                node.append(div_1)
