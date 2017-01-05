# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # working on one record at a time seems faster... Maybe it should not work in chunks...
    util.recompute_fields(cr, 'sale.order', ['delivery_price'], chunk_size=1)
