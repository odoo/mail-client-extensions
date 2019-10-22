# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "stock.inventory.line", "product_barcode")
    util.remove_field(cr, "stock.inventory", "scan_location_id")
    util.remove_field(cr, "stock.inventory", "_barcode_scanned")  # from barcode mixin

    util.remove_view(cr, "stock_barcode.stock_inventory_view_form_inherit_stock_barcode")
