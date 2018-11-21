# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking.type", "barcode")
    util.remove_view(cr, "stock_barcode.stock_picking_type_view_form_barcode")
