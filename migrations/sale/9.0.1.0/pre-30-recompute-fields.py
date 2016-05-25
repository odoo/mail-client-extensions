# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'tax subtotal total'.split():
        util.create_column(cr, 'sale_order_line', 'price_' + f, 'numeric')
