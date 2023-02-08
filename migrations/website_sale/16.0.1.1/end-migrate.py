# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT id
          FROM ir_ui_view
         WHERE key = 'website_sale.product'
           AND website_id IS NOT NULL
        """
    )
    for view_id in cr.fetchall():
        with util.edit_view(cr, view_id=view_id) as arch:
            for node in arch.xpath('//div[@id="wrap"][not(hasclass("o_wsale_product_page"))]'):
                node.attrib["class"] = (node.attrib.get("class", "") + " o_wsale_product_page").lstrip()
