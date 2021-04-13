# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    inventory_availability = env["ir.default"].get("product.template", "inventory_availability")
    env["ir.default"].set("product.template", "allow_out_of_stock_order", inventory_availability == "never")
    env["ir.default"].set("product.template", "show_availability", inventory_availability != "never")
    util.remove_field(cr, "res.config.settings", "inventory_availability")
    util.remove_field(cr, "product.template", "inventory_availability")
