# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'stock.config.settings', 'module_delivery_temando')

    util.remove_field(cr, 'stock.quant.package', 'parent_left')
    util.remove_field(cr, 'stock.quant.package', 'parent_right')

    util.remove_view(cr, 'stock.external_layout_barcode_right')
    util.remove_view(cr, 'stock.external_layout_header_barcode_right')
