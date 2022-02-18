# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "iface_orderline_customer_notes")
    util.remove_field(cr, "pos.config", "iface_display_categ_images")
    util.remove_field(cr, "pos.config", "tax_regime")
    util.remove_field(cr, "pos.config", "product_configurator")
    util.remove_field(cr, "pos.config", "module_account")
    util.remove_field(cr, "pos.config", "allowed_pricelist_ids")
    util.remove_field(cr, "pos.config", "selectable_categ_ids")
    util.remove_field(cr, "pos.order", "invoice_group")
