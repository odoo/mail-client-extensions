# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "stock_picking_batch.stock_picking_to_batch_action")
