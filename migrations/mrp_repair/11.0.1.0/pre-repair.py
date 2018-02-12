# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Add the repair_id on the stock_move
    util.create_column(cr, 'stock_move', 'repair_id', 'int4')
    cr.execute(""" 
        UPDATE stock_move m
        SET repair_id = r.id
        FROM mrp_repair r
        WHERE r.move_id = m.id
    """)
    cr.execute(""" 
        UPDATE stock_move m
        SET repair_id = rl.repair_id
        FROM mrp_repair_line rl
        WHERE rl.move_id = m.id
    """)
    # Add stock move lines to repair stock moves
    cr.execute("""INSERT INTO stock_move_line
                    (product_id, location_id, location_dest_id, product_uom_qty, qty_done, product_uom_id, 
                        owner_id, date, lot_id, move_id, state)
                    SELECT product_id, location_id, location_dest_id, 0.0, product_uom_qty, product_uom, 
                        restrict_partner_id, date, restrict_lot_id, id, state
                    FROM stock_move 
                    WHERE repair_id IS NOT NULL""") #lot_id should come from restrict_lot_id
    
    # Consumed/produced stock_move_line link
    cr.execute("""INSERT INTO stock_move_line_consume_rel
                     (produce_line_id, consume_line_id)
                SELECT ml1.id, ml2.id FROM mrp_repair r, stock_move m1, stock_move m2, stock_move_line ml1, stock_move_line ml2
                WHERE m1.repair_id = r.id AND m2.repair_id = r.id AND ml1.move_id = m1.id AND ml2.move_id = m2.id
                    AND m1.product_id != r.product_id AND m2.product_id = r.product_id
    """)