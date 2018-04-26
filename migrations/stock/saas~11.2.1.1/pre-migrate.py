# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'product_name product_code location_name prodlot_name'.split():
        util.remove_field(cr, 'stock.inventory.line', f)
