# -*- coding: utf-8 -*-
import logging
from openerp.addons.base.maintenance.migrations import util

COUNT = 0
_logger = logging.getLogger(__name__)

def merge_moves(cr, first_one, to_delete, total_qty, total_uom_qty):
    global COUNT
    # This method is used to merge stock moves, but at the same time preserve the information on the old models,
    # so we can use them later for e.g. splitting the stock_pack_operation_lot into stock_move_line
    cr.execute("""UPDATE stock_move SET product_qty = %s, product_uom_qty = %s WHERE id = %s""", (total_qty, total_uom_qty, first_one)) # Needs to calculate product_qty and state too
    cr.execute("""INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
                    SELECT %s, mr.move_dest_id FROM stock_move_move_rel mr
                    WHERE mr.move_orig_id IN %s
                    GROUP BY mr.move_dest_id
                    ON CONFLICT DO NOTHING
    """, (first_one, tuple(to_delete)))

    cr.execute("""INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
                    SELECT mr.move_orig_id, %s FROM stock_move_move_rel mr
                    WHERE mr.move_dest_id IN %s
                    GROUP BY mr.move_orig_id
                    ON CONFLICT DO NOTHING
    """, (first_one, tuple(to_delete)))

    COUNT += 1
    BATCH_SIZE = 100000
    if COUNT % BATCH_SIZE == 0:
        _logger.info("Commit changes after %s lines updated, batch #%s", BATCH_SIZE, int(COUNT / BATCH_SIZE))
        cr.execute("REINDEX TABLE stock_move_line")
        cr.commit()

    cr.execute("""UPDATE stock_move_line SET move_id = %s WHERE move_id IN %s""", (first_one, tuple(to_delete)))
    cr.execute("""UPDATE stock_move_operation_link SET move_id = %s WHERE move_id IN %s""",
               (first_one, tuple(to_delete)))
    cr.execute(
        """
            INSERT INTO stock_quant_move_rel(quant_id, move_id)
                 SELECT quant_id, %s
                   FROM stock_quant_move_rel
                  WHERE move_id IN %s
            ON CONFLICT DO NOTHING
        """, (first_one, tuple(to_delete),)
    )
    cr.execute("""DELETE FROM stock_quant_move_rel WHERE move_id IN %s""", (tuple(to_delete),))
    cr.execute("""UPDATE stock_quant SET reservation_id  = %s WHERE reservation_id IN %s""",
               (first_one, tuple(to_delete)))
    # Adapt state
    cr.execute("""SELECT state FROM stock_move WHERE id IN %s""", (tuple(to_delete) + (first_one,),))
    res = cr.fetchall()
    states = [re[0] for re in res]
    if not any(x in ('done', 'cancel', 'draft') for x in states):
        state = 'confirmed'
        if all(x == 'assigned' for x in states):
            state = 'assigned'
        elif any(x in ('assigned', 'partially_available') for x in states):
            state = 'partially_available'
        elif any(x == 'waiting' for x in states):
            state = 'waiting'
        cr.execute("""UPDATE stock_move SET state = %s WHERE id = %s """, (state, first_one,))
    cr.execute("""DELETE FROM stock_move WHERE id IN %s""", (tuple(to_delete),))


def create_idx(cr):
    idx_list = [
        ("procurement_order_move_dest_id_mig_idx", "procurement_order", "move_dest_id"),
        ("stock_move_consumed_for_mig_idx", "stock_move", "consumed_for"),
        ("stock_move_origin_returned_move_id_mig_idx", "stock_move", "origin_returned_move_id"),
        ("stock_move_split_from_mig_idx", "stock_move", "split_from"),
        ("stock_quant_negative_move_id_mig_idx", "stock_quant", "negative_move_id"),
    ]
    for idx_name, table_name, column_name in idx_list:
        util.create_index(cr, idx_name, table_name, column_name)
    cr.execute("ANALYZE stock_move")


def migrate(cr, version):
    create_idx(cr)

    # Remove ir cron scheduler action as it will be on procurement group instead of procurement order
    util.remove_record(cr, 'stock.ir_cron_scheduler_action')

    # Remove views
    util.remove_view(cr, 'stock.view_move_form')
    util.remove_view(cr, 'stock.view_pack_operation_details_form')

    # clean the stock.move.operation.link table (kind of m2m)
    cr.execute("""
        DELETE FROM stock_move_operation_link l
         WHERE NOT EXISTS (SELECT 1 FROM stock_pack_operation WHERE id = l.operation_id)
            OR NOT EXISTS (SELECT 1 FROM stock_move WHERE id = l.move_id)
    """)

    # Create column lot_id/lot_name on stock_pack_operation, product_qty is renamed to product_uom_qty to be consistent with stock.move
    util.create_column(cr, 'stock_pack_operation', 'lot_id', 'int4')
    util.create_column(cr, 'stock_pack_operation', 'lot_name', 'varchar')
    util.rename_field(cr, 'stock.pack.operation', 'product_qty', 'product_uom_qty')
    # Add move_id column as every move_line/pack op will only have one move
    util.create_column(cr, 'stock_pack_operation', 'move_id', 'int4')

    # For the pack operations that moved an entire pack in done pickings, we need to explode them and link to the foreseen move
    cr.execute("""
        INSERT INTO stock_pack_operation (move_id, product_id, location_id, location_dest_id, product_uom_qty, qty_done, product_uom_id,
            fresh_record, package_id, result_package_id, owner_id, picking_id, ordered_qty, date, lot_id, lot_name)
        SELECT m.id, m.product_id, p.location_id, p.location_dest_id, 0.0, SUM(l.qty), pt.uom_id,
            'f', p.package_id, p.package_id, p.owner_id, p.picking_id, 0, m.date, q.lot_id, NULL
        FROM stock_pack_operation p, stock_move_operation_link l, stock_move m, product_product pp, product_template pt, stock_picking pick, stock_quant q
        WHERE p.product_id IS NULL AND p.package_id IS NOT NULL AND pp.id = m.product_id AND pt.id = pp.product_tmpl_id
            AND pick.id = p.picking_id AND pick.state = 'done' AND l.move_id = m.id AND q.id = l.reserved_quant_id AND l.operation_id = p.id
        GROUP BY m.id, l.operation_id, q.lot_id, p.id, pt.uom_id
    """) #Could be extra checked by stock_quant_move_rel

    # For the pack operations that would be moving an entire picking in open pickings, we can depend on quants in the package to split into stock.move.line
    cr.execute("""
        INSERT INTO stock_pack_operation (product_id, location_id, location_dest_id, product_uom_qty, qty_done, product_uom_id,
            fresh_record, package_id, result_package_id, owner_id, picking_id, ordered_qty, date, lot_id, lot_name)
        SELECT q.product_id, op.location_id, op.location_dest_id, 0.0, CASE WHEN op.qty_done > 0 THEN SUM(q.qty) ELSE 0.0 END, pt.uom_id,
            'f', pack.id, pack.id, op.owner_id, pick.id, 0, op.date, q.lot_id, NULL
        FROM stock_quant_package pack, stock_pack_operation op, stock_picking pick, stock_quant q,
            product_product pp, product_template pt
        WHERE op.product_id IS NULL AND op.package_id IS NOT NULL
            AND op.package_id = pack.id AND pick.id = op.picking_id AND q.package_id = pack.id
            AND pick.state not in ('done', 'cancel') AND pp.id = q.product_id AND pt.id = pp.product_tmpl_id
        GROUP BY q.product_id, q.lot_id, pack.id, op.id, pt.uom_id, pick.id
    """) #qty_done depends on whether it has already been checked (as being picked) or not

    # We delete the original pack operations that moved the entire package as these don't exist anymore in v11 (or are magically calculated on the fly in an extra field)
    cr.execute("""
        DELETE FROM stock_pack_operation WHERE product_id IS NULL
    """)

    # Rename pack operation to stock move line (could have done so earlier)
    util.rename_model(cr, 'stock.pack.operation', 'stock.move.line')
    util.create_column(cr, 'stock_move_line', 'product_qty', 'numeric')
    cr.execute ("""UPDATE stock_move_line ml SET product_qty = 0, product_uom_qty = 0
                   FROM stock_move m, stock_location l, product_template pt, product_product p
                   WHERE ml.picking_id IS NULL
                   AND p.product_tmpl_id = pt.id
                   AND m.product_id = p.id
                   AND ml.move_id = m.id
                   AND m.location_id = l.id
                   AND NOT (pt.type = 'consu' AND m.state = 'assigned')
                   AND NOT (l.usage IN ('supplier', 'production', 'inventory') AND m.state = 'assigned')""")

    cr.execute("""UPDATE stock_move_line ml SET product_qty = 0, product_uom_qty = 0
                  FROM stock_picking p, stock_location l, product_template pt, product_product pr
                  WHERE ml.picking_id = p.id
                  AND pr.product_tmpl_id = pt.id
                  AND ml.product_id = pr.id
                  AND p.location_id = l.id
                  AND NOT (pt.type = 'consu' AND p.state = 'assigned')
                  AND NOT (l.usage IN ('supplier', 'production', 'inventory') AND p.state = 'assigned')""")

    # Pack operations will appear for every (done) move, so this won't always be in a picking
    cr.execute("""ALTER TABLE stock_move_line ALTER COLUMN picking_id DROP NOT NULL""")

    # Add some indexes to improve speed when we will merge moves.
    # maybe only when #stock_moves > 10000 (could also delete constraints)
    for name, table, columns in [
        ("stock_move_orig", "stock_move", ("origin_returned_move_id",)),
        ("procurement_move_dest_id", "procurement_order", ("move_dest_id",)),
        ("stock_move_split_from", "stock_move", ("split_from", "state")),
        ("stock_move_operation_link_move_id", "stock_move_operation_link", ("move_id",)),
        ("stock_quant_negative_move_id", "stock_quant", ("negative_move_id",)),
        ("stock_scrap_move_id", "stock_scrap", ("move_id",)),
        ("stock_move_lots_move_id", "stock_move_lots", ("move_id",)),
        ("stock_valuation_adjustment_lines_move_id", "stock_valuation_adjustment_lines", ("move_id",)),
    ]:
        util.create_index(cr, name, table, *columns)
    # Use a hash index because they behave better for updates, in merge_moves we run many queries like
    # UPDATE stock_move_line SET move_id = %s WHERE move_id IN %s
    # which are extremely slow since they use and modify the index
    cr.execute("CREATE INDEX stock_move_line_move_id_upg_idx ON stock_move_line USING hash(move_id)")
    cr.execute("ANALYZE stock_move_line")

    util.fixup_m2m(cr, "stock_quant_move_rel", "stock_move", "stock_quant", "move_id", "quant_id")

    cr.commit()
    # Update: partially_available state has been removed from picking
    cr.execute("""UPDATE stock_picking SET state='assigned' WHERE state='partially_available'""")
    # But added to the stock_move
    cr.execute("""UPDATE stock_move SET state='partially_available' WHERE partially_available='t' AND state in ('confirmed', 'waiting')""")

    # The move_orig_ids, move_dest many2one for chained moves,
    # together with the split_from needs to be replaced by a many2many
    util.create_m2m(cr, 'stock_move_move_rel', 'stock_move', 'stock_move', 'move_orig_id', 'move_dest_id')
    # First: make the m2m chained links for those where it is easy (no split_froms)
    cr.execute("""
        INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
        SELECT id, move_dest_id FROM stock_move m
        WHERE m.move_dest_id IS NOT NULL AND m.split_from IS NULL
            AND m.state != 'cancel'
            AND NOT EXISTS (SELECT id FROM stock_move m2 WHERE m2.split_from = m.id AND m2.state != 'cancel')""")

    # Second: start from the original moves that have been split (for backorders e.g.)
    # Then for every one of these moves, search the split_froms recursively (in case of backorder of backorder e.g.)
    # Make links between split_froms and all their dests and original chained moves
    cr.execute("""SELECT id, picking_id FROM stock_move m
                    WHERE m.split_from IS NULL
                     AND m.state != 'cancel' AND picking_id IS NOT NULL
                     AND EXISTS (SELECT id FROM stock_move m2 WHERE m2.split_from = m.id AND m2.state != 'cancel')""")
    res = cr.fetchall()
    for re in res:
        dests = [re[0]]
        split_froms = [re[0]]
        picking_moves = {re[1]: [re[0]]}
        while split_froms:
            split_from = split_froms.pop()
            cr.execute("""
                SELECT id, picking_id FROM stock_move WHERE split_from=%s AND state != 'cancel'
            """, (split_from,))
            res2 = cr.fetchall()
            for re2 in res2: #Normally, there is only one
                dests.append(re2[0])
                split_froms.append(re2[0])
                picking_moves.setdefault(re2[1], [])
                picking_moves[re2[1]].append(re2[0])
        cr.execute("""
            INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
            SELECT m2.id, m1.id FROM stock_move m1, stock_move m2
            WHERE m1.id IN %s AND m2.move_dest_id IN %s
             AND NOT EXISTS (SELECT move_orig_id FROM stock_move_move_rel r2
                            WHERE r2.move_orig_id = m2.id AND r2.move_dest_id = m1.id)
            GROUP BY m1.id, m2.id
        """, (tuple(dests), tuple(dests)))
        cr.execute("""
            INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
            SELECT m1.id, m2.id FROM stock_move m1, (SELECT move_dest_id AS id FROM stock_move WHERE id in %s AND move_dest_id IS NOT NULL) m2
            WHERE m1.id IN %s AND NOT EXISTS (SELECT move_orig_id FROM stock_move_move_rel r2
                                                WHERE r2.move_orig_id = m1.id AND r2.move_dest_id = m2.id)
            GROUP BY m1.id, m2.id
        """, (tuple(dests), tuple(dests)))

        # We can remerge when picking is the same (as the split was propagated from a previous picking to next pickings in the chain and this is not done anymore in v11)
        for pick in picking_moves:
            if len(picking_moves[pick]) > 1:
                # As it is a split_from, the UoM of the quantities stays the same
                cr.execute("""SELECT SUM(product_qty), SUM(product_uom_qty)
                                 FROM stock_move
                                 WHERE id IN %s AND state != 'cancel' GROUP BY product_id """, (tuple(picking_moves[pick]),))
                sums = cr.fetchall()[0]
                merge_moves(cr, picking_moves[pick][0], picking_moves[pick][1:], sums[0], sums[1])

    # The same many2many links are also used for returns now
    cr.execute("""
        INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
        SELECT origin_returned_move_id, id FROM stock_move
        WHERE origin_returned_move_id IS NOT NULL
    """)

    # Merge moves logic: in v11, we try to avoid as much as possible to have 2 moves of the same product in a picking
    # We need to keep split e.g. if it is a return or linked to different sale/purchase order line or linked to different lot/serial number
    # This should follow the same logic as the merge_moves logic in the code
    query_string = """SELECT COUNT(*) OVER (PARTITION BY m.picking_id, m.product_id,
                            CASE WHEN m.state = 'done' THEN 1
                                 WHEN m.state = 'draft' THEN 2
                                 ELSE 3 END,
                            m.price_unit, m.restrict_lot_id, m.product_packaging, m.procure_method,
                            m.product_uom, m.restrict_partner_id, m.scrapped, m.origin_returned_move_id"""
    if util.column_exists(cr, 'stock_move', 'purchase_line_id'):
        query_string += ", m.purchase_line_id"
    if util.column_exists(cr, 'procurement_order', 'sale_line_id'):
        query_string += ", proc.sale_line_id"
    query_string += """ ),  m.id, COALESCE(m.product_qty, m.product_uom_qty), m.product_uom_qty, m.picking_id, m.product_id, m.state, m.price_unit, m.product_packaging, m.procure_method,
                             m.product_uom, m.restrict_partner_id, m.scrapped, m.origin_returned_move_id
                    FROM stock_move m
                    LEFT JOIN procurement_order proc ON m.procurement_id = proc.id
                    WHERE m.picking_id IS NOT NULL AND m.state != 'cancel'
                    ORDER BY m.picking_id, m.product_id, m.state, m.price_unit, m.product_packaging, m.procure_method,
                            m.product_uom, m.restrict_partner_id, m.scrapped, m.origin_returned_move_id"""
    if util.column_exists(cr, 'stock_move', 'purchase_line_id'):
        query_string += ", m.purchase_line_id"
    if util.column_exists(cr, 'procurement_order', 'sale_line_id'):
        query_string += ", proc.sale_line_id"
    cr.execute(query_string)
    res = cr.fetchall()
    # The query partitions by the moves we can merge, so we go through all records and after each partition > 1 we merge
    count = 0
    to_delete = []
    total_qty = 0
    total_uom_qty = 0
    first_one = False
    for re in res:
        if count > 0:
            total_qty += re[2]
            total_uom_qty += re[3]
            to_delete.append(re[1])
        if count == 1.0:
            merge_moves(cr, first_one, to_delete, total_qty, total_uom_qty)
            to_delete = []
        if not count:
            if re[0] == 1:
                continue
            count = re[0]
            total_qty = re[2]
            total_uom_qty = re[3]
            first_one = re[1]
        count -= 1

    # create temp table to allow // execute
    cr.execute(
        """
        SELECT picking_id,
               product_id,
               max(id) AS id
          INTO UNLOGGED _upg_pick_product
          FROM stock_move
         WHERE picking_id IS NOT NULL
         GROUP BY picking_id, product_id
        HAVING COUNT(*) = 1
        """
    )
    cr.execute("CREATE UNIQUE INDEX _upg_pick_product_pk_idx ON _upg_pick_product (id)")
    cr.execute("CREATE INDEX ON _upg_pick_product (picking_id, product_id)")
    cr.execute(
        """
           ALTER TABLE _upg_pick_product
        ADD CONSTRAINT _upg_pick_product_pkey
           PRIMARY KEY
           USING INDEX _upg_pick_product_pk_idx
        """
    )

    # Link stock.move and stock.move.line when there is only one move in the picking (easy case)
    util.explode_execute(
        cr,
        """
          UPDATE stock_move_line
             SET move_id = pick_product.id
            FROM _upg_pick_product AS pick_product
           WHERE stock_move_line.product_id = pick_product.product_id
             AND stock_move_line.picking_id = pick_product.picking_id
        """,
        table="stock_move_line",
    )
    # drop temp table
    cr.execute("DROP TABLE _upg_pick_product")

    # Scrapped needs move lines too
    cr.execute("""INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
            package_id, owner_id, picking_id, date, lot_id, move_id)
            SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.product_uom_qty, m.product_uom,
                s.package_id, m.restrict_partner_id, NULL, m.date, m.restrict_lot_id, m.id
            FROM stock_move m, stock_scrap s WHERE scrapped='t' AND s.move_id = m.id
    """)

    cr.execute("""INSERT INTO stock_move_line
        (product_id, location_id, location_dest_id, product_qty, product_uom_qty, qty_done, product_uom_id,
            owner_id, picking_id, date, lot_id, move_id)
            SELECT m.product_id, m.location_id, m.location_dest_id, 0.0, 0.0, m.product_uom_qty, m.product_uom,
                m.restrict_partner_id, NULL, m.date, m.restrict_lot_id, m.id
            FROM stock_move m
            WHERE m.scrapped = 't' AND NOT EXISTS (SELECT id FROM stock_scrap WHERE move_id = m.id)
    """) #v8/v9 scraps did not get an added stock_scrap object (not in migration scripts)

    # Company_id on quants should be stored related field with the company of the location, so it should be false in virtual locations
    # So it should be able to be null
    cr.execute("""ALTER TABLE stock_quant ALTER COLUMN company_id DROP NOT NULL""")
    # Create quants in supplier, production, inventory locations
    cr.execute("""INSERT INTO stock_quant (product_id, lot_id, package_id, location_id, owner_id, qty, company_id, in_date)
                    SELECT q.product_id, q.lot_id, NULL, m.location_id, m.restrict_partner_id, -SUM(q.qty), NULL, MIN(date)
                    FROM stock_quant q, stock_quant_move_rel sqmr, stock_move m, stock_location l
                    WHERE sqmr.move_id =  m.id AND sqmr.quant_id = q.id
                        AND m.location_id = l.id AND l.usage IN ('supplier', 'production', 'inventory')
                        AND m.state = 'done'
                    GROUP BY q.product_id, q.lot_id, m.location_id, m.restrict_partner_id""")


    # min_date/max_date on test_picking -> faster in sql than in migration
    util.create_column(cr, 'stock_picking', 'scheduled_date', 'timestamp without time zone')
    util.explode_execute(
        cr,
        """
        UPDATE stock_picking
           SET scheduled_date = CASE WHEN move_type = 'direct' THEN min_date ELSE max_date END
        """,
        table="stock_picking",
    )
    oldfields = util.splitlines("""
        min_date
        max_date
        launch_pack_operations
        pack_operation_product_ids
        quant_reserved_exist
        pack_operation_ids
        recompute_pack_op
        pack_operation_pack_ids
        pack_operation_exist
    """)
    for f in oldfields:
        util.remove_field(cr, 'stock.picking', f)

    util.create_column(cr, 'stock_move', 'reference', 'varchar')
    util.explode_execute(
        cr,
        """
        UPDATE stock_move m SET reference = p.name
            FROM stock_picking p
            WHERE m.picking_id = p.id
        """,
        table="stock_move",
        alias="m",
    )
    util.explode_execute(
        cr,
        """
        UPDATE stock_move m SET reference = m.name
        WHERE m.picking_id IS NULL
        """,
        table="stock_move",
        alias="m",
    )

    util.create_column(cr, 'stock_move_line', 'reference', 'varchar')
    util.create_column(cr, 'stock_move_line', 'state', 'varchar')
    util.explode_execute(
        cr,
        """
        UPDATE stock_move_line ml
        SET state = m.state, reference = m.reference
        FROM stock_move m
        WHERE ml.move_id = m.id
        """,
        table="stock_move_line",
        alias="ml",
    )

    # remove hash index
    cr.execute("DROP INDEX stock_move_line_move_id_upg_idx")
    util.create_index(cr, "stock_move_line_move_id", "stock_move_line", "move_id")
    cr.commit()
