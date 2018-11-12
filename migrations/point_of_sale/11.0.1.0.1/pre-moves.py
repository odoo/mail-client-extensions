# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
        package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, state)
        SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.product_uom_qty, m.product_uom,
            NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, NULL, m.id, m.state
        FROM stock_move m, pos_order_line pol
        WHERE pol.name = m.name AND pol.product_id = m.product_id 
            AND m.picking_id IS NULL AND m.state ='done'
            AND NOT EXISTS (SELECT move_id FROM stock_move_line ml WHERE ml.move_id = m.id)
    """)