# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Add columns
    util.create_column(cr, 'stock_move_line', 'done_wo', 'bool')
    util.create_column(cr, 'stock_move_line', 'production_id', 'int4')
    util.create_column(cr, 'stock_move_line', 'workorder_id', 'int4')
    util.create_column(cr, 'stock_move_line', 'lot_produced_id', 'int4')

    # Sometimes there are stock_move_lots without quantity_done (maybe because they changed from tracked to non-tracked) and it is better to delete them
    cr.execute("""
        DELETE FROM stock_move_lots WHERE done_move = 't' AND quantity_done is null;
    """)

    # Tracked moves in production orders, those with stock_move_lots, need to be converted to stock.move.line
    cr.execute("""
        INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
        package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, done_wo, state, workorder_id,
        lot_produced_id, production_id)
        SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, l.quantity_done, m.product_uom,
        NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, l.lot_id, m.id, l.done_wo, m.state, l.workorder_id,
        l.lot_produced_id, l.production_id
        FROM stock_move_lots l, stock_move m, product_product p, product_template pt
        WHERE l.move_id = m.id AND p.id = m.product_id AND p.product_tmpl_id = pt.id
    """)

    # Non-tracked moves are those without stock.move.lots and those need to get stock.move.line too
    # If the finished product is tracked, those need to have a lot_produced_id too!
    cr.execute("""
            INSERT INTO stock_move_line
            (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
            package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, done_wo, state, lot_produced_id)
            SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, ml.quantity_done * m.unit_factor, m.product_uom,
                NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, NULL, m.id, 't', m.state, ml.lot_id
            FROM stock_move m, mrp_production p, stock_move mf, stock_move_lots ml
            WHERE m.raw_material_production_id = p.id AND mf.production_id = p.id
                AND mf.product_id = p.product_id AND ml.move_id = mf.id
                AND p.state NOT IN ('done', 'cancel')
                AND m.state NOT IN ('done', 'cancel')
                AND NOT EXISTS (SELECT id FROM stock_move_lots ml2 WHERE ml2.move_id = m.id)
    """)

    # Log an error when quantity_done_store != SUM (quantity_done)
    cr.execute("""
            SELECT m.id FROM stock_move m, stock_move_line ml, mrp_production p  
            WHERE ml.move_id = m.id AND m.raw_material_production_id IS NOT NULL
                AND p.id = m.raw_material_production_id
                AND p.state NOT IN ('done', 'cancel')
                AND EXISTS (SELECT ml2.id FROM stock_move_lots ml2, stock_move m2 
                            WHERE ml2.move_id = m2.id AND m2.production_id = p.id
                                AND p.product_id = m2.product_id)
                AND NOT EXISTS (SELECT id FROM stock_move_lots mlo WHERE mlo.move_id = m.id) 
            GROUP BY m.id
            HAVING SUM(ml.qty_done) != m.quantity_done_store
    """)
    res = cr.fetchall()
    if res:
        _logger.warning('There are moves in production orders where the theoretical quantities do not match: %s', res)

    # For the other lines
    cr.execute("""
        INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
        package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, done_wo, state)
        SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.product_uom_qty, m.product_uom,
            NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, NULL, m.id, 't', m.state
        FROM stock_move m, product_product p, product_template pt
        WHERE (m.raw_material_production_id IS NOT NULL OR m.production_id IS NOT NULL OR m.consume_unbuild_id IS NOT NULL OR m.unbuild_id IS NOT NULL)
         AND p.id = m.product_id and p.product_tmpl_id = pt.id
         AND NOT EXISTS (SELECT move_id FROM stock_move_line ml WHERE ml.move_id = m.id) AND m.state ='done'
    """)
    #quantity_done_store should be used only when state is not done, cancel (could be merged with previous query however, but don't forget quantity_done_store > 0)
    cr.execute("""
            INSERT INTO stock_move_line
            (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
            package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, done_wo, state)
            SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.quantity_done_store, m.product_uom,
                NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, NULL, m.id, 't', m.state
            FROM stock_move m, product_product p, product_template pt
            WHERE (m.raw_material_production_id IS NOT NULL OR m.production_id IS NOT NULL OR m.consume_unbuild_id IS NOT NULL OR m.unbuild_id IS NOT NULL)
             AND p.id = m.product_id and p.product_tmpl_id = pt.id
             AND NOT EXISTS (SELECT move_id FROM stock_move_line ml WHERE ml.move_id = m.id) AND m.state not in ('done', 'cancel')
             AND m.quantity_done_store > 0.0
        """)

    # Links between consumed and produced move lines
    cr.execute("""
         INSERT INTO stock_move_line_consume_rel
         (produce_line_id, consume_line_id)
         SELECT megajoin.ml1, megajoin.ml2 FROM
         (SELECT ml1.id as ml1, ml2.id as ml2 FROM stock_quant_consume_rel sqcr, stock_move m1, stock_move m2, stock_move_line ml1, stock_move_line ml2, stock_quant q1, stock_quant q2,
         stock_quant_move_rel sqmr1, stock_quant_move_rel sqmr2
         WHERE sqcr.consume_quant_id = q1.id AND sqmr1.quant_id = q1.id AND sqmr1.move_id = m1.id AND ml1.move_id = m1.id AND (ml1.lot_id IS NULL OR ml1.lot_id = q1.lot_id)
          AND sqcr.produce_quant_id = q2.id AND sqmr2.quant_id = q2.id AND sqmr2.move_id = m2.id AND ml2.move_id = m2.id AND (ml2.lot_id IS NULL OR ml2.lot_id = q2.lot_id)
          AND ((m1.raw_material_production_id IS NOT NULL AND m2.production_id IS NOT NULL) OR (m1.consume_unbuild_id IS NOT NULL AND m2.unbuild_id IS NOT NULL)) GROUP BY ml1.id, ml2.id
         ) megajoin
    """) # Produce_line_id and consume_line_id were opposite in the mode
    # Temporary move lines are avoided as the moves are not done normally