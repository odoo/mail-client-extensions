# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.immediate.transfer", "pick_to_backorder_ids")
    cr.execute("DROP TABLE stock_immediate_transfer_stock_picking_rel")
