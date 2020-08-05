# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = ['price_tax', 'price_subtotal', 'price_total']
    cr.execute("SELECT id FROM sale_order_line WHERE price_total IS NULL ORDER BY product_id")
    ids = [r[0] for r in cr.fetchall()]
    util.recompute_fields(cr, 'sale.order.line', fields, chunk_size=500, ids=ids)
    cr.execute("update sale_order_line set price_reduce=price_subtotal/product_uom_qty where coalesce(product_uom_qty,0)!=0")
    cr.execute("update sale_order_line set price_reduce=0 where product_uom_qty=0")
