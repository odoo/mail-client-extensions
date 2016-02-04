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

    env = util.env(cr)
    cr.execute("SELECT id FROM sale_order")
    orders = env['sale.order'].browse([x[0] for x in cr.fetchall()])
    orders._recompute_todo(orders._fields['delivery_price'])
    orders.recompute()
