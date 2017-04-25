# -*- coding: utf-8 -*-
from operator import itemgetter

from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = ['price_tax', 'price_subtotal', 'price_total']
    cr.execute('SELECT id FROM "sale_order_line" order by product_id')
    ids = map(itemgetter(0), cr.fetchall())
    util.recompute_fields(cr, 'sale.order.line', fields, chunk_size=500)
    cr.execute("update sale_order_line set price_reduce=price_subtotal/product_uom_qty where coalesce(product_uom_qty,0)!=0")
    cr.execute("update sale_order_line set price_reduce=0 where product_uom_qty=0")
