# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # depending on what was set in the config, we might want the consu/product products to be invoiced on delivery by default
    env = util.env(cr)
    order_policy = env['ir.values'].get_default('sale.order', 'order_policy')
    if order_policy == 'picking':
        cr.execute("""UPDATE product_template SET invoice_policy='delivery' WHERE type in ('product','consu')""")
