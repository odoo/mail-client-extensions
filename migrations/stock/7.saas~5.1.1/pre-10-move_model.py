# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_model(cr, 'stock.location.path', 'stock_location', 'stock')

