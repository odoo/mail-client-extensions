# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def get_modules():
    # list saas-6 delivery modules that are maybe installed
    return ['delivery'] + ['delivery_%s' % d for d in 'fedex temando ups'.split()]

def migrate(cr, version):
    # should only run when the last delivery module is updated
    cr.execute("""
        SELECT count(1)
          FROM ir_module_module
         WHERE name = ANY(%s)
           AND state = 'to upgrade'
    """, [get_modules()])
    if cr.fetchone()[0] != 1:
        # there are still modules to upgrade
        return

    # working on one record at a time seems faster... Maybe it should not work in chunks...
    util.recompute_fields(cr, 'sale.order', ['delivery_price'], chunk_size=1)
