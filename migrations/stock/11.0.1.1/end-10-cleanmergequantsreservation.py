# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    # Update reserved quantity on stock move line where reservations on split quants correspond
    cr.execute("""
        UPDATE stock_move_line move_line SET product_qty = mega.qty
        FROM
            (SELECT SUM(q.quantity) AS qty, ml.id AS ml_id
                FROM stock_quant q, stock_move m, stock_move_line ml
                WHERE ml.move_id = m.id AND q.reservation_id = m.id
                    AND ml.product_id = q.product_id AND ml.location_id = q.location_id
                    AND (ml.lot_id = q.lot_id or (ml.lot_id IS NULL AND q.lot_id IS NULL) 
                        OR (q.lot_id IS NULL AND ml.lot_id IS NOT NULL
                            AND NOT EXISTS (SELECT id FROM stock_move_line ml2 
                                                        WHERE ml.id != ml2.id 
                                                            AND ml2.move_id = m.id AND ml2.product_id = ml.product_id 
                                                            AND ml2.location_id = ml.location_id AND ml2.lot_id IS NULL
                                                            AND (ml2.owner_id = ml.owner_id OR (ml.owner_id IS NULL AND ml2.owner_id IS NULL))
                                                            AND (ml2.package_id = ml.package_id OR (ml.package_id IS NULL AND ml2.package_id IS NULL))
                                                            )))
                    AND (ml.owner_id = q.owner_id OR (ml.owner_id IS NULL AND q.owner_id IS NULL)) 
                    AND (ml.package_id = q.package_id OR (ml.package_id IS NULL AND q.package_id IS NULL))
                GROUP BY m.id, ml.id, q.product_id, q.location_id, q.lot_id, q.owner_id, q.package_id) mega
        WHERE mega.ml_id = move_line.id
    """) # SUM can not be higher than what is foreseen on move

    # Search quants reserved without move line and create move lines for them
    cr.execute("""
        INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
                                owner_id, date, lot_id, move_id, picking_id, state)
        SELECT q.product_id, q.location_id, mres.location_dest_id, SUM(q.quantity), 0.0, 0.0, mres.product_uom,
                                q.owner_id, mres.date, q.lot_id, mres.id, mres.picking_id, mres.state
        FROM stock_quant q, stock_move mres
        WHERE q.reservation_id = mres.id AND NOT EXISTS
            (SELECT ml.id
            FROM stock_move m, stock_move_line ml
            WHERE ml.move_id = m.id AND q.reservation_id = m.id
                AND ml.product_id = q.product_id AND ml.location_id = q.location_id
                AND (ml.lot_id = q.lot_id or (ml.lot_id IS NULL AND q.lot_id IS NULL)
                    OR (q.lot_id IS NULL AND ml.lot_id IS NOT NULL
                        AND NOT EXISTS (SELECT id FROM stock_move_line ml2
                                                    WHERE ml.id != ml2.id
                                                        AND ml2.move_id = m.id AND ml2.product_id = ml.product_id
                                                        AND ml2.location_id = ml.location_id AND ml2.lot_id IS NULL
                                                        AND (ml2.owner_id = ml.owner_id OR (ml.owner_id IS NULL AND ml2.owner_id IS NULL))
                                                        AND (ml2.package_id = ml.package_id OR (ml.package_id IS NULL AND ml2.package_id IS NULL))
                                                        )))
                AND (ml.owner_id = q.owner_id OR (ml.owner_id IS NULL AND q.owner_id IS NULL))
                AND (ml.package_id = q.package_id OR (ml.package_id IS NULL AND q.package_id IS NULL))
        ) GROUP BY mres.id, q.product_id, q.location_id, q.owner_id, q.lot_id, q.package_id
    """)

    # Calculate product_uom_qty on stock_move_line from product_qty
    cr.execute("""
        UPDATE  stock_move_line move_line
        SET     product_uom_qty
                = round(move_line.product_qty * puom.factor / muom.factor,
                        ceil(-log(puom.rounding))::integer)
        FROM    product_product prod
        ,       product_uom muom
        ,       product_template temp
        ,       product_uom puom
        WHERE   prod.id = move_line.product_id
        AND     temp.id = prod.product_tmpl_id
        AND     muom.id = temp.uom_id
        AND     puom.id = move_line.product_uom_id
        AND     product_qty > 0.0;
    """)

    cr.execute(""" UPDATE stock_quant SET reserved_quantity = quantity WHERE reservation_id IS NOT NULL""")
    util.remove_model(cr, 'procurement.order')
    util.remove_model(cr, 'stock.history')
    util.remove_model(cr, 'stock.move.lots')
    util.remove_model(cr, 'stock.move.operation.link')
    util.remove_model(cr, 'make.procurement')
    util.remove_model(cr, 'wizard.valuation.history')


    util.remove_field(cr, 'stock_quant', 'propagated_from_id')
    util.remove_field(cr, 'stock_quant', 'negative_move_id')
    util.remove_field(cr, 'stock_quant', 'reservation_id')
    util.remove_field(cr, 'stock_quant', 'packaging_type_id')
    util.remove_field(cr, 'stock_quant', 'cost')

    util.remove_field(cr, 'stock_move', 'move_dest_id')
    util.remove_field(cr, 'stock_move', 'procurement_id')
    util.remove_field(cr, 'stock_move', 'partially_available')
    util.remove_field(cr, 'stock_move', 'split_from')
    util.remove_field(cr, 'stock_move', 'restrict_lot_id')
    # Use super-efficient merge algo, but also adjust for in_date
    cr.execute("""WITH
                        dupes AS (
                            SELECT min(id) as to_update_quant_id,
                                (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)] as to_delete_quant_ids,
                                SUM(reserved_quantity) as reserved_quantity,
                                SUM(quantity) as quantity,
                                MIN(in_date) as min_in_date
                            FROM stock_quant
                            GROUP BY product_id, company_id, location_id, lot_id, package_id, owner_id
                            HAVING count(id) > 1
                        ),
                        _up AS (
                            UPDATE stock_quant q
                                SET quantity = d.quantity,
                                    reserved_quantity = d.reserved_quantity,
                                    in_date = min_in_date
                            FROM dupes d
                            WHERE d.to_update_quant_id = q.id
                        )
                   DELETE FROM stock_quant WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
        """)
    # Remove quants for consumables
    cr.execute("""
        DELETE FROM stock_quant q USING product_product p, product_template pt
            WHERE pt.type = 'consu' AND p.id = q.product_id AND pt.id = p.product_tmpl_id
    """)

    # Create stock_move_line for stock moves done without
    cr.execute("""INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
        package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, state)
        SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.product_uom_qty, m.product_uom,
            NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, NULL, m.id, m.state
        FROM stock_move m
        WHERE m.state = 'done' AND m.inventory_id IS NULL AND m.product_qty > 0.0 
            AND NOT EXISTS (SELECT id FROM stock_move_line WHERE move_id = m.id) 
        RETURNING move_id, picking_id, product_id
    """)
    res = cr.fetchall()
    if res:
        _logger.warning('We added some stock move line for move (move, picking, product): %s', res)
    # compute state on move line if not set already
    cr.execute("""
    UPDATE stock_move_line ml
    SET state = m.state
    FROM stock_move m
    WHERE ml.move_id = m.id and ml.state is null;
    """)

    # As date of migrated pack operations had no real meaning before, while it should be the date now
    cr.execute("""
        UPDATE stock_move_line SET date = m.date
            FROM stock_move m
            WHERE move_id = m.id AND m.state = 'done' AND m.picking_id IS NOT NULL
    """)
