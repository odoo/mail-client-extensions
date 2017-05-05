# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'purchase.config.settings', 'po_lead')

    util.create_column(cr, 'purchase_order', 'invoice_count', 'int4')
    util.create_column(cr, 'purchase_order', 'picking_count', 'int4')

    util.create_m2m(cr, 'account_invoice_purchase_order_rel', 'purchase_order', 'account_invoice')
    util.create_m2m(cr, 'purchase_order_stock_picking_rel', 'purchase_order', 'stock_picking')

    cr.execute("""
        INSERT INTO account_invoice_purchase_order_rel(purchase_order_id, account_invoice_id)
             SELECT DISTINCT ol.order_id, il.invoice_id
               FROM account_invoice_line il
               JOIN purchase_order_line ol ON (ol.id = il.purchase_line_id)
    """)

    cr.execute("""
        INSERT INTO purchase_order_stock_picking_rel(purchase_order_id, stock_picking_id)
    SELECT DISTINCT l.order_id,
                    unnest(array_remove(array_cat(ARRAY[m.picking_id], array_agg(r.picking_id)), NULL))
              FROM stock_move m
              JOIN purchase_order_line l ON (l.id = m.purchase_line_id)
         LEFT JOIN stock_move r ON (r.origin_returned_move_id = m.id)
             WHERE m.state != 'cancel'
               AND coalesce(r.state, '') != 'cancel'
          GROUP BY m.picking_id, l.order_id

    """)

    cr.execute("""
        UPDATE purchase_order o
           SET invoice_count = (SELECT count(1)
                                  FROM account_invoice_purchase_order_rel
                                 WHERE purchase_order_id = o.id),
               picking_count = (SELECT count(1)
                                  FROM purchase_order_stock_picking_rel
                                 WHERE purchase_order_id = o.id)
    """)
