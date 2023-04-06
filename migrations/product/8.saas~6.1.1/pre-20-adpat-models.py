# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.drop_depending_views(cr, 'product_uom', 'uom_type')
    util.rename_field(cr, "product.product", "ean13", "barcode")
    util.rename_field(cr, "product.template", "ean13", "barcode")
