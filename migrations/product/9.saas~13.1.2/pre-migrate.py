# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'product.property_product_pricelist', True)

    # ensure uom constraint can be set
    cr.execute("UPDATE product_uom SET rounding=0.001 WHERE coalesce(rounding, 0) = 0")
    cr.execute("UPDATE product_uom SET rounding=abs(rounding)")

    util.remove_field(cr, 'product.template', 'product_manager')
