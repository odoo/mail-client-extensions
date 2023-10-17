# -*- coding: utf-8 -*-
from functools import lru_cache

from lxml import etree

from odoo.tools import misc

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
            for node in arch.xpath('//t[@t-call="website_sale.shop_product_carousel"]'):
                # There are multiple divs with class='row' that have no unique ids, so
                # it's difficult to obtain a particular div reliably. Instead, we obtain
                # a unique (to this template) node of the div that interests us and
                # refer to its parent
                updated_node = get_node()
                parent = node.getparent()
                parent.getparent().replace(parent, updated_node)


@lru_cache(1)
def get_node():
    with misc.file_open("website_sale/views/templates.xml") as fp:
        tree = etree.parse(fp)
        node = tree.find("//template[@id='product']//div[@id='product_detail_main']")
        if node is not None:
            return node
    raise RuntimeError("Node not found")
