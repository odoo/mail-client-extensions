# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.move_field_to_module(cr, "product.template", "optional_product_ids", "sale", "sale_product_configurator")
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.product_product_1_product_template"))
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.product_product_4_product_template"))
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.product_product_11_product_template"))
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.optional_products_modal"))
    util.rename_xmlid(cr,  *eb("sale{.product_configurator_,_product_configurator.}configure"))
    util.rename_xmlid(cr,  *eb("sale{.product_configurator_,_product_configurator.}configure_optional_products"))
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.optional_product_items"))
    util.rename_xmlid(cr,  *eb("sale{,_product_configurator}.sale_product_configurator_view_form"))
