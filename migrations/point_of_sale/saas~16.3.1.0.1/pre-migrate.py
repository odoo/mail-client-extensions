# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "limited_products_loading")
    util.remove_field(cr, "pos.config", "limited_products_amount")
    util.remove_field(cr, "pos.config", "product_load_background")
    util.remove_field(cr, "pos.config", "limited_partners_loading")
    util.remove_field(cr, "pos.config", "limited_partners_amount")
    util.remove_field(cr, "pos.config", "partner_load_background")

    util.remove_field(cr, "res.config.settings", "pos_limited_products_loading")
    util.remove_field(cr, "res.config.settings", "pos_limited_products_amount")
    util.remove_field(cr, "res.config.settings", "pos_product_load_background")
    util.remove_field(cr, "res.config.settings", "pos_limited_partners_loading")
    util.remove_field(cr, "res.config.settings", "pos_limited_partners_amount")
    util.remove_field(cr, "res.config.settings", "pos_partner_load_background")

    if util.module_installed(cr, "pos_restaurant"):
        util.delete_unused(cr, "pos_restaurant.kitchen_printer")
        util.move_field_to_module(cr, "pos.config", "printer_ids", "pos_restaurant", "point_of_sale")
        util.move_field_to_module(cr, "pos.config", "is_order_printer", "pos_restaurant", "point_of_sale")
        util.move_model(cr, "restaurant.printer", "pos_restaurant", "point_of_sale", move_data=True)
        util.rename_model(cr, "restaurant.printer", "pos.printer")
        util.rename_xmlid(cr, *eb("point_of_sale.view_{restaurant,pos}_printer_form"))
        util.rename_xmlid(cr, *eb("point_of_sale.action_{restaurant,pos}_printer_form"))
        util.rename_xmlid(cr, *eb("point_of_sale.view_{restaurant,pos}_printer"))

    util.remove_view(cr, "point_of_sale.qunit_suite_assets")
    util.remove_view(cr, "point_of_sale.assets_common")

    util.remove_model(cr, "pos.session.check_product_wizard")
