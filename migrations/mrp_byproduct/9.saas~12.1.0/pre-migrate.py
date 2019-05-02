# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "mrp.subproduct", "product_uom", "product_uom_id")
    util.remove_field(cr, "mrp.subproduct", "subproduct_type")
