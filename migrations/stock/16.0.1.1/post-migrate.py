# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    inconsistencies.verify_uoms(cr, "stock.move", uom_field="product_uom")
    util.recompute_fields(cr, "stock.move", ["quantity_done"])
