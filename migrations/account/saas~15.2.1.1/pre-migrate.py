# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "account.move", "partner_shipping_id", "sale", "account")
    util.move_field_to_module(cr, "res.config.settings", "group_delivery_invoice_address", "sale", "account")
