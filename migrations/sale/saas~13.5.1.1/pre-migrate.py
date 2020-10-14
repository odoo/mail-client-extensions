# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("sale.access_product_product_attribute_custom_value{,_sale_manager}"))

    util.remove_view(cr, "sale.attribute_tree_view")
    util.remove_view(cr, "sale.product_template_attribute_line_form")
    util.remove_view(cr, "sale.product_attribute_view_form")
    util.remove_view(cr, "sale.product_template_attribute_value_view_tree_inherit")
    util.remove_view(cr, "sale.product_template_attribute_value_view_form_inherit")
