# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "product.product", "price")
    util.remove_field(cr, "product.product", "pricelist_id")

    util.remove_field(cr, "product.template", "price")
    util.remove_field(cr, "product.template", "pricelist_id")
