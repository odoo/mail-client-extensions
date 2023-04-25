# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Search for cases where we have multiple moves for the same product in a picking

    cr.execute(
        """
        SELECT m.picking_id,
               m.product_id,
               bool_or(l.id IS NOT NULL)
          FROM stock_move m
          JOIN stock_picking p
            ON m.picking_id = p.id

     LEFT JOIN stock_move_line op
            ON op.product_id = m.product_id
           AND op.picking_id = p.id
     LEFT JOIN stock_pack_operation_lot l
            ON l.operation_id = op.id

         WHERE NOT m.scrapped
         GROUP BY m.picking_id, m.product_id, p.id
        HAVING COUNT(*) > 1
        """
    )
    res = cr.fetchall()
    for re in res:
        # Check moves / move lines related to the same product in the picking
        picking = util.env(cr)['stock.picking'].browse(re[0])
        moves = picking.move_lines.filtered(lambda x: x.product_id.id == re[1] and not x.scrapped)
        move_lots = {}
        # If we track the product by lot, we need to check the quants moved for every move to see which lots were moved for dividing the stock.pack.operation.lot
        if re[2]:
            # Get minimum rounding or 0.00001 if no rounding
            cr.execute("SELECT COALESCE(-log(min(rounding)),5) FROM product_uom");
            rounding = cr.fetchone()[0]
            if picking.state == 'done':
                cr.execute("""SELECT sqmr.move_id, q.lot_id, ROUND(SUM(q.quantity):: numeric,%s::int)
                            FROM stock_quant_move_rel sqmr, stock_quant q
                            WHERE sqmr.quant_id = q.id AND sqmr.move_id IN %s
                            GROUP BY sqmr.move_id, q.lot_id""", (rounding, tuple(moves.ids),))
            else:
                cr.execute("""SELECT m.id, q.lot_id, ROUND(SUM(q.quantity):: numeric,%s::int)
                            FROM stock_move m, stock_quant q
                            WHERE q.reservation_id = m.id AND m.id IN %s
                            GROUP BY m.id, q.lot_id""", (rounding, tuple(moves.ids),))
            mqs = cr.fetchall()
            for mq in mqs:
                move_lots.setdefault(mq[0], {})
                move_lots[mq[0]][mq[1]] = mq[2]
            for move in moves:
                for ml in move.move_line_ids:
                    if move.id in move_lots and move_lots[move.id].get(ml.lot_id.id):
                        move_lots[move.id][ml.lot_id.id] -= ml.product_qty
        
        # Use operation links between moves and move_lines to assign move_line to move and maybe split them
        for move in moves:
            cr.execute("""SELECT operation_id, sum(qty) from stock_move_operation_link where move_id = %s group by move_id, operation_id""", (move.id,))
            links = cr.fetchall()
            for link in links:
                operation = util.env(cr)['stock.move.line'].browse(link[0])
                try:
                    product_qty = operation.product_uom_id._compute_quantity(operation.qty_done, operation.product_id.uom_id)
                except:
                    _logger.warning('UoM conversion failed for operation %s, product %s, picking %s between %s and %s',
                                    operation.id, move.product_id.display_name, picking.name,
                                    operation.product_uom_id.name, operation.product_id.uom_id.name)
                    continue
                if link[1] >= product_qty or move.state != 'done':
                    operation.move_id = move.id
                else:
                    try:
                        qty = operation.product_id.uom_id._compute_quantity(link[1], operation.product_uom_id)
                    except:
                        _logger.warning('UoM conversion failed for operation %s, product %s, picking %s between %s and %s',
                                        operation.id, move.product_id.display_name, picking.name,
                                        operation.product_id.uom_id.name, operation.product_uom_id.name)
                        continue
                    product_uom_qty = operation.qty_done
                    
                    #op2 = operation.copy(default={'product_uom_qty': 0.0,
                    #                              'qty_done': qty})
                    cr.execute("""
                    INSERT INTO stock_move_line (move_id, product_id, location_id, location_dest_id, product_uom_qty, qty_done, product_uom_id, 
        fresh_record, package_id, result_package_id, owner_id, picking_id, ordered_qty, date, lot_id, lot_name, state) 
             (SELECT  %s, p.product_id,  p.location_id, p.location_dest_id, 0.0, %s, p.product_uom_id, 
                        p.fresh_record, p.package_id, p.result_package_id, p.owner_id, p.picking_id, p.ordered_qty, p.date, p.lot_id, p.lot_name, p.state
                    FROM stock_move_line p WHERE id = %s) RETURNING id
                    """, (move.id, qty, operation.id,))
                    op2 = cr.fetchall()[0][0]
                    
                    # Compare pack operation lots
                    cr.execute("""SELECT id, qty, lot_id FROM stock_pack_operation_lot 
                                    WHERE operation_id = %s""", (operation.id,))
                    packlots = cr.fetchall()
                    to_match_afterwards = []
                    # Assign the right pack operation lots to this operation (which will later be converted to stock_move_line and will have the right move then)
                    for packlot in packlots:
                        matched_qty = move_lots.get(move.id, {}).get(packlot[2], 0.0)
                        matched_qty_packopized = operation.product_id.uom_id._compute_quantity(matched_qty, operation.product_uom_id)
                        packlot_normalized = operation.product_uom_id._compute_quantity(packlot[1], operation.product_id.uom_id)
                        if matched_qty:
                            if packlot[1] <= matched_qty_packopized:
                                #Set packlot's move line (as they will be converted afterwards
                                cr.execute("""UPDATE stock_pack_operation_lot SET operation_id = %s WHERE id = %s""", (op2, packlot[0]))
                                move_lots[move.id][packlot[2]] -= packlot_normalized
                            else:
                                # split stock_pack_operation_lot
                                qty = matched_qty_packopized
                                remaining_qty = packlot[1] - qty
                                cr.execute("""INSERT INTO stock_pack_operation_lot 
                                                (lot_id, lot_name, qty_todo, qty, operation_id)
                                            SELECT lot_id, lot_name, %s, %s, %s 
                                            FROM stock_pack_operation_lot WHERE id = %s 
                                """, (qty, qty, op2, packlot[0]))
                                cr.execute("""UPDATE stock_pack_operation_lot SET qty = %s, qty_todo = %s WHERE id = %s""", (remaining_qty, remaining_qty, packlot[0]))
                                move_lots[move.id][packlot[2]] -= matched_qty
                    if product_uom_qty < qty:
                        _logger.warning("Rounding errors for splitting operation %s: %s vs. %s ", operation.id, product_uom_qty, qty)
                    cr.execute("""UPDATE stock_move_line SET qty_done = %s WHERE id = %s""",
                               (product_uom_qty - qty if product_uom_qty > qty else 0.0, operation.id)) #rounding errors, in sql, otherwise quants get changed
                    util.env(cr)['stock.move.line'].invalidate_cache()


    # Convert the (adapted) stock_pack_operation_lots into stock_move_line and delete their original stock_move_line
    util.explode_execute(
        cr,
        """
        INSERT INTO stock_move_line
                    (move_id, product_id, location_id, location_dest_id, product_uom_qty, qty_done, product_uom_id, 
                    fresh_record, package_id, result_package_id, owner_id, picking_id, ordered_qty, date, lot_id, 
                    lot_name, state) 
             SELECT p.move_id, p.product_id,  p.location_id, p.location_dest_id, l.qty, l.qty, p.product_uom_id,
                    p.fresh_record, p.package_id, p.result_package_id, p.owner_id, p.picking_id, p.ordered_qty, coalesce(pp.date, p.date), l.lot_id,
                    l.lot_name, m.state
               FROM stock_move_line p
               JOIN stock_pack_operation_lot l
                 ON p.id = l.operation_id
               JOIN stock_picking pp
                 ON pp.id = p.picking_id
               JOIN stock_move m 
                 ON m.id = p.move_id
        """,
        table="stock_move_line",
        alias="p",
    )
    
    cr.execute(
        """
        WITH info AS (
            SELECT operation_id
              FROM stock_pack_operation_lot
          GROUP BY operation_id
        ) DELETE FROM stock_move_line l
                USING info
                WHERE l.id=info.operation_id
        """
    )

    # Check if there are still procurement exceptions without move related
    cr.execute("""
        SELECT count(*) FROM procurement_order WHERE state='exception' AND move_dest_id IS NULL;
    """)
    res = cr.fetchall()
    if res:
        _logger.warning("Procurements in Exception not generated by a move could give problems (e.g. confirmed SO line in error): %s", res)
