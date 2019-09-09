# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "product.template", "weight_uom_id")
    util.move_field_to_module(cr, "product.pricelist", "discount_policy", "sale", "product")
