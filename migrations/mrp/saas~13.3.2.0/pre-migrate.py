# -*- coding: utf-8 -*-
from odoo.upgrade import util

def migrate(cr, version):
    util.remove_field(cr, 'stock.move.line', 'lot_produced_qty')
