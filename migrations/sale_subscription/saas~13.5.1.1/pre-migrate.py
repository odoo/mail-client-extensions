# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription", "partner_invoice_id", "int4")
    util.create_column(cr, "sale_subscription", "partner_shipping_id", "int4")
