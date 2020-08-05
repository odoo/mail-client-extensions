# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # working on one record at a time seems faster... Maybe it should not work in chunks...
    cr.execute("SELECT id FROM sale_order WHERE delivery_price IS NULL")
    ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, 'sale.order', ['delivery_price'], chunk_size=1, ids=ids)
