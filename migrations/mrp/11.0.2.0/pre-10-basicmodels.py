# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):
    # Add columns
    util.create_column(cr, 'stock_move_line', 'done_wo', 'bool', default=None)  # force default to NULL
    util.create_column(cr, 'stock_move_line', 'production_id', 'int4')
    util.create_column(cr, 'stock_move_line', 'workorder_id', 'int4')
    util.create_column(cr, 'stock_move_line', 'lot_produced_id', 'int4')
    util.create_column(cr, 'stock_move_line', 'done_move', 'bool')

    # Sometimes there are stock_move_lots without quantity_done (maybe because they changed from tracked to non-tracked) and it is better to delete them
    cr.execute("""
        DELETE FROM stock_move_lots WHERE done_move = 't' AND quantity_done is null;
    """)

    queries = []
    # Tracked moves in production orders, those with stock_move_lots, need to be converted to stock.move.line
    queries.append("""
        INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
        package_id, result_package_id, owner_id, picking_id, date, lot_id, move_id, done_wo, state, workorder_id,
        lot_produced_id, production_id)
        SELECT m.product_id, m.location_id, m.location_dest_id, l.quantity, 0.0,
        CASE WHEN m.state = 'done' THEN l.quantity_done ELSE 0.0 END, m.product_uom,
        NULL, NULL, m.restrict_partner_id, m.picking_id, m.date, l.lot_id, m.id, l.done_wo, m.state, l.workorder_id,
        l.lot_produced_id, l.production_id
        FROM stock_move_lots l, stock_move m, product_product p, product_template pt
        WHERE l.move_id = m.id AND p.id = m.product_id AND p.product_tmpl_id = pt.id
    """)

    # Non-tracked moves are those without stock.move.lots and those need to get stock.move.line too
    # If the finished product is tracked, those need to have a lot_produced_id too!
    queries.append("""
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
    util.parallel_execute(cr, queries)

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

    _logger.info("Creating links between consumed and produced move lines (megajoin)")
    # Make inserts in stock_move_line_consume_rel to track products

    with util.temp_index(
        cr, "stock_move", "raw_material_production_id"
    ), util.temp_index(cr, "stock_move", "production_id"):
        util.explode_execute(
            cr,
            """INSERT INTO stock_move_line_consume_rel (produce_line_id, consume_line_id)
               SELECT sml1.id sml1, sml2.id sml2
                 FROM mrp_production mp
                 JOIN stock_move sm1 ON sm1.raw_material_production_id = mp.id
                 JOIN stock_move_line sml1 ON sm1.id = sml1.move_id
                 JOIN stock_move sm2 ON sm2.production_id = mp.id
                 JOIN stock_move_line sml2 ON sm2.id = sml2.move_id
                 JOIN product_product pp ON (pp.id = sml1.product_id OR pp.id = sml2.product_id)
                 JOIN product_template pt ON pt.id = pp.product_tmpl_id
                WHERE mp.state = 'done'
                  AND pt.tracking <> 'none'
                  AND {parallel_filter}
             GROUP BY sml1.id, sml2.id
            """,
            table="mrp_production",
            alias="mp",
            bucket_size=200,
        )

    cr.execute("""
        UPDATE stock_move_line  ml
           SET done_move=m.is_done
          FROM stock_move m
         WHERE m.id=ml.move_id
    """)
