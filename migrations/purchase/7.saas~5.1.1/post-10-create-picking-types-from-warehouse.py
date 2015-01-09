# -*- coding: utf-8 -*-
# performs various checks and try to fix the errors automatically

import logging

import openerp
from openerp.addons.base.maintenance.migrations import util

_logger = logging.getLogger(__name__)

def sanitize_pickings_from_warehouse(cr):
    registry = openerp.modules.registry.RegistryManager.get(cr.dbname)
    picking = registry['stock.picking']
    picking_type = registry['stock.picking.type']

    # NOTE: column purchase.lot_input_id created in:
    #       stock/7.saas~5/pre-05-various-checks.py

    # 1. create picking type based on main warehouse picking type but change
    #    the destination location to match the warehouse input location that
    #    has been deleted
    cr.execute("""
        SELECT  lot_input_id
        ,       location.name
        ,       main_picking_type.id AS base_picking_type
        ,       array_agg(purchase.id)
        FROM    purchase_order purchase
        JOIN    stock_location location
        ON      location.id = lot_input_id
        JOIN    stock_picking_type main_picking_type
        ON      main_picking_type.warehouse_id = purchase.warehouse_id
        AND     main_picking_type.code = 'incoming'
        WHERE   lot_input_id IS NOT NULL
        GROUP BY lot_input_id, purchase.warehouse_id, location.id,
                 main_picking_type.id
        """)
    for lot_input, name, base_picking_type, purchases in cr.fetchall():
        _logger.warn(
            "[Picking type created based on id=%s, %s purchases updated] "
            "the original warehouse was used to handle a different "
            "location.", base_picking_type, len(purchases))
        new_picking_type = picking_type.copy(
            cr, openerp.SUPERUSER_ID, base_picking_type, {
                'default_location_dest_id': lot_input,
                'name': name,
            })
        # 1.1. update the purchase's picking_type_id to this new picking type
        cr.execute("""
            UPDATE purchase_order SET picking_type_id = %s WHERE id = ANY(%s)
                RETURNING id
            """, [new_picking_type, purchases])
        _logger.warn("[Picking type of %s purchase orders changed to %s] %s",
                     cr.rowcount, new_picking_type,
                     ", ".join([str(x) for x, in cr.fetchall()]))
        # 1.2. update stock moves with the new picking type
        cr.execute("""
            WITH my_moves AS (
                SELECT  move.id
                FROM    purchase_order purchase
                JOIN    purchase_order_line line
                ON      line.order_id = purchase.id
                JOIN    stock_move move
                ON      move.purchase_line_id = line.id
                WHERE   purchase.id = ANY(%s)
            )
            UPDATE  stock_move
            SET     picking_type_id = %s
            WHERE   id IN (SELECT * FROM my_moves)
            RETURNING id
            """, [purchases, new_picking_type])
        if cr.rowcount:
            _logger.warn("[Picking type of %s moves changed to %s] %s",
                         cr.rowcount, new_picking_type,
                         ", ".join([str(x) for x, in cr.fetchall()]))
        # 1.3. update picking_type_id of purchases' pickings
        cr.execute("""
            WITH my_pickings AS (
                SELECT  move.picking_id
                FROM    stock_move move
                WHERE   move.picking_type_id = %s
                GROUP BY move.picking_id
            )
            UPDATE  stock_picking
            SET     picking_type_id = %s
            WHERE   id IN (SELECT * FROM my_pickings)
            RETURNING id
            """, [new_picking_type, new_picking_type])
        if cr.rowcount:
            _logger.warn("[Picking type of %s pickings changed to %s] %s",
                         cr.rowcount, new_picking_type,
                         ", ".join([str(x) for x, in cr.fetchall()]))

    # 2. update other purchases to get the warehouse's picking type
    cr.execute("""
        UPDATE  purchase_order
        SET     picking_type_id = main_picking_type.id
        FROM    purchase_order purchase
        JOIN    stock_picking_type main_picking_type
        ON      main_picking_type.warehouse_id = purchase.warehouse_id
        AND     main_picking_type.code = 'incoming'
        WHERE   purchase.id = purchase_order.id
        AND     purchase.lot_input_id IS NULL
        """)

    # 3. drop the temporary column
    cr.execute("ALTER TABLE purchase_order DROP COLUMN lot_input_id")

def migrate(cr, version):
    if util.column_exists(cr, 'purchase_order', 'lot_input_id'):
        sanitize_pickings_from_warehouse(cr)
