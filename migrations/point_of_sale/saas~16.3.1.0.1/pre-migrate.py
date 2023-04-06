# -*- coding: utf-8 -*-
from odoo.upgrade import util


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
