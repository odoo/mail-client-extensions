# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
INSERT INTO stock_move_line	
    (move_id, product_id, product_uom_id, product_qty, product_uom_qty, qty_done, lot_id, owner_id, package_id, result_package_id, state,	
     location_id, location_dest_id, date, reference)
SELECT 
    m.id,
    m.product_id,
    m.product_uom,
    0.0,
    0.0,
    m.product_qty,
    m.restrict_lot_id,
    m.restrict_partner_id,
    CASE WHEN il.theoretical_qty>il.product_qty 
       THEN il.package_id
       ELSE NULL
    END,
    CASE WHEN il.theoretical_qty<il.product_qty 
       THEN il.package_id
       ELSE NULL
    END,
    'done',
    m.location_id,
    m.location_dest_id,
    m.date,
    m.name
FROM stock_inventory_line il
     INNER JOIN stock_inventory i ON il.inventory_id = i.id
     INNER JOIN stock_move m ON m.inventory_id = il.inventory_id AND m.product_id = il.product_id AND m.product_uom = il.product_uom_id
     INNER JOIN stock_location l1 ON l1.id = m.location_id
     INNER JOIN stock_location l2 ON l2.id = m.location_dest_id
WHERE i.state = 'done'
  AND (
        (il.theoretical_qty>il.product_qty AND l1.usage!='inventory' AND l2.usage='inventory')
        OR (il.theoretical_qty<il.product_qty AND l1.usage='inventory'  AND l2.usage!='inventory')
      )
  AND m.product_uom_qty=abs(il.theoretical_qty-il.product_qty)
  AND (
        (il.prod_lot_id IS NULL AND m.restrict_lot_id IS NULL) 
        OR (il.prod_lot_id IS NOT NULL AND il.prod_lot_id=m.restrict_lot_id)
      )
  AND (
        (il.partner_id IS NULL AND m.restrict_partner_id IS NULL)
        OR (il.partner_id IS NOT NULL AND il.partner_id=m.restrict_partner_id)
      )
  AND NOT EXISTS (SELECT id FROM stock_move_line sl WHERE sl.move_id = m.id) 
    """)
