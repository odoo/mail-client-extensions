# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock_barcode.stock_picking_view_form_inherit_stock_barcode")
    util.remove_view(cr, "stock_barcode.view_barcode_lot_form")
    util.remove_view(cr, "stock_barcode.view_barcode_lot_kanban")
    util.remove_inherit_from_model(cr, "stock.move.line", "barcodes.barcode_events_mixin")
    util.remove_inherit_from_model(cr, "stock.picking", "barcodes.barcode_events_mixin")
    util.remove_model(cr, "stock_barcode.lot")
    util.remove_model(cr, "stock_barcode.lot.line")
