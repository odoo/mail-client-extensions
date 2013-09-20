# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    util.create_column(cr, 'account_invoice_line', 'purchase_line_id', 'int4')

    cr.execute("""
        UPDATE account_invoice_line il

           SET purchase_line_id = pl.id

          FROM purchase_invoice_rel rel, purchase_order_line pl
         WHERE il.invoice_id = rel.invoice_id
           AND pl.order_id = rel.purchase_id

           AND il.name = pl.name
           AND il.price_unit = pl.price_unit
           AND il.quantity = pl.product_qty
           AND coalesce(il.product_id, 0) = coalesce(pl.product_id, 0)
           AND coalesce(il.uos_id, 0) = coalesce(pl.product_uom, 0)
           AND coalesce(il.account_analytic_id, 0) = coalesce(pl.account_analytic_id, 0)
    """)
