import collections
import itertools
import logging
import math
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

from odoo import sql_db

from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies

ODOO_UPG_14_PARALLEL_WORKORDER_CREATION = util.str2bool(os.environ.get("ODOO_UPG_14_PARALLEL_WORKORDER_CREATION", "0"))

_logger = logging.getLogger("odoo.upgrade.mrp.134" + __name__)


# cannot be defined locally, because it needs to be serializable through "pickle" for ProcessPoolExecutor
def _create_workorder_cb(mp_ids):
    # init upon first call. Done here instead of initializer callback, becaue py3.6 doesn't have it
    if not hasattr(_create_workorder_cb, "env"):
        sql_db._Pool = None  # children cannot borrow from copies of the same pool, it will cause protocol error
        _create_workorder_cb.env = util.env(sql_db.db_connect(_create_workorder_cb.dbname).cursor())
        _create_workorder_cb.env.clear()
    # process
    _create_workorder_cb.env["mrp.production"].browse(mp_ids)._create_workorder()
    _create_workorder_cb.env.cr.commit()


def migrate(cr, version):
    # Migration for PR: odoo/odoo#52949 and odoo/enterprise#11149, task_id: 2241471
    util.remove_column(cr, "mrp_routing_workcenter", "old_id")
    # Remove old operation
    cr.execute("DELETE FROM mrp_routing_workcenter WHERE bom_id IS NULL")
    cr.execute(
        """
        DROP TABLE IF EXISTS mrp_workorder_line CASCADE;
        DROP TABLE IF EXISTS mrp_routing CASCADE;
        DROP TABLE IF EXISTS temp_new_mrp_operation CASCADE;
        """
    )
    _logger.info("Generate missing `move_finished_ids` for draft MOs")
    env = util.env(cr)
    cr.execute("SELECT id FROM mrp_production WHERE state = 'draft'")
    draft_mo_ids = [res[0] for res in cr.fetchall()]
    for mo in util.iter_browse(env["mrp.production"], draft_mo_ids, strategy="commit"):
        mo.with_company(mo.company_id)._onchange_move_finished_product()

    # The first part of the migration script is to fill the new `qty_producing` field.
    # There are multiple cases to handle:
    #   1. if the production order is done, use the sum of `qty_done` of the finished move lines
    #   2. if the production order is not done and doesn't contain any done move, use the sum the
    #      `qty_done` of the finished move lines and delete them
    #   3. if the production order contains done move, create "backordered" productions with the
    #      done move and refer to the previous use case to handle the non-done moves.
    # NOTE : this part will set `qty_producing` even on production orders having multiple lots or
    #       serials produced, and these productions will be split into multiple ones in the next
    #       parts (the new paradigm is one production equals one production order when traceability
    #       is involved).

    # (1./3.) Set qty_producing for all MO to be equals to the quantity produced (done)
    _logger.info("Set qty_producing in MO with done move")
    cr.execute(
        """
        WITH mo_qty_producing AS (
            SELECT mp.id AS mo_id, sum(sml.qty_done / uom_sml.factor * uom_mp.factor) AS qty_producing
              FROM stock_move_line sml
                   JOIN stock_move AS sm ON sml.move_id = sm.id
                   JOIN mrp_production AS mp ON sm.production_id = mp.id
                   LEFT JOIN uom_uom AS uom_sml ON sml.product_uom_id = uom_sml.id
                   LEFT JOIN uom_uom AS uom_mp ON mp.product_uom_id = uom_mp.id
             WHERE sml.product_id = mp.product_id
                   AND mp.state IN ('progress', 'to_close', 'done')
                   AND sm.state = 'done'
                   AND sml.qty_done > 0
          GROUP BY mp.id
        )
        UPDATE mrp_production
           SET qty_producing = mo_qty_producing.qty_producing
          FROM mo_qty_producing
         WHERE mrp_production.id = mo_qty_producing.mo_id
     RETURNING mrp_production.id, mrp_production.company_id
        """
    )
    ids_to_backorder_by_company = defaultdict(list)
    for production_id, company_id in cr.fetchall():
        ids_to_backorder_by_company[company_id].append(production_id)

    # (3.) For MO in progress with the done move
    _logger.info("Create backorder for in progress MO")
    for company_id, ids_to_backorder in ids_to_backorder_by_company.items():
        for mos in util.iter_browse(env["mrp.production"], ids_to_backorder, strategy="commit", chunk_size=50):
            mos = mos.filtered(lambda mo: mo.state != "done" and mo._get_quantity_to_backorder() > 0)
            mos.with_company(company_id)._generate_backorder_productions(close_mo=True)
            for mo in mos:
                mo.product_qty = mo.qty_producing

    # (2.)
    _logger.info("Remove move line of unfinished MO and set qty_producing on it")
    cr.execute(
        """
        WITH mo_without_finished_move_done AS (
          SELECT DISTINCT mp.id AS mo_id
            FROM mrp_production AS mp
                 JOIN stock_move AS sm ON (sm.production_id = mp.id AND mp.product_id = sm.product_id)
           WHERE sm.state NOT IN ('done', 'cancel') AND mp.state NOT IN ('done', 'cancel')
        ),
        delete_slm AS (
            DELETE FROM stock_move_line AS sml
             USING stock_move AS sm
                   JOIN mo_without_finished_move_done AS mo ON sm.production_id = mo.mo_id
             WHERE sml.move_id = sm.id
         RETURNING sml.move_id, sml.qty_done, sml.product_uom_id
        ),
        mo_qty_producing AS (
            SELECT mp.id AS mo_id, sum(sml.qty_done / uom_sml.factor * uom_mp.factor) AS qty_producing
              FROM delete_slm sml
                   JOIN stock_move AS sm ON sml.move_id = sm.id
                   JOIN mrp_production AS mp ON sm.production_id = mp.id
                   LEFT JOIN uom_uom AS uom_sml ON sml.product_uom_id = uom_sml.id
                   LEFT JOIN uom_uom AS uom_mp ON mp.product_uom_id = uom_mp.id
             WHERE mp.state != 'done' AND sm.state NOT IN ('cancel', 'done')
          GROUP BY mp.id
        )
        UPDATE mrp_production
           SET qty_producing = mo_qty_producing.qty_producing
          FROM mo_qty_producing
         WHERE mrp_production.id = mo_qty_producing.mo_id
        """
    )

    # The second part of the migration is to split production orders where multiple lots or serials
    # where produced into different ones for each lot or serial.
    # 1) Find manufacturing orders which should be split (`temp_mo_backorder_info`)
    # 2) For each finished lot, we get back their stock move and stock move line consumed (`temp_mrp_consumed_line`)
    # 3) Create the backordered orders as a copy of the source order
    #    (expect for backorder_sequence, lot_producing_id, name, product_qty, qty_producing)
    # 4) With the information found at 2), as previously a single stock move was used to produce
    #    multiple lot, we need to split them into the new backordered productions. We decrease their
    #    original quantity and duplicate them across new backorders.
    # 5) We don't have this issue for the stock move lines, as they were already separated for each
    #    produced lots, so we just move them into the related new move.
    # NOTE : For now, we don't split workorder. In the current case, workorders will be only on the first MO (X-001)
    #        Unfortunately, now the cost analysis and the stock valuation layers are inconsistent with MO
    #        (and backorder created). If we want to split workorder: the time_ids (mrp.workcenter.productivity) and
    #        dates fields need to split/relink, recreate m2m, relink stock_move to workorder, etc
    util.create_column(cr, "mrp_production", "old_id", "int4")
    util.create_column(cr, "stock_move", "old_id", "int4")
    column_production = util.get_columns(
        cr,
        "mrp_production",
        ignore=("id", "old_id", "lot_producing_id", "backorder_sequence", "name", "product_qty", "qty_producing"),
    )
    column_production_pre = [f"mp.{c}" for c in column_production]
    column_stock_move = util.get_columns(
        cr,
        "stock_move",
        ignore=("id", "old_id", "product_uom_qty", "production_id", "raw_material_production_id"),
    )
    column_stock_move_pre = [f"sm.{c}" for c in column_stock_move]
    if not util.table_exists(cr, "temp_mo_backorder_info"):
        # (1.) temp_mo_backorder_info : source mo id, finished lot id, qty by backorder, backorder sequence
        _logger.info("Create backorder info temporary table")
        cr.execute(
            """
            WITH mo_id_lot_id AS (
                SELECT DISTINCT mp.id AS mo_id,
                       mp.product_uom_id AS mo_uom_id,
                       spl.id AS lot_id
                  FROM mrp_production mp
                       JOIN product_product AS pp ON mp.product_id = pp.id
                       JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
                       JOIN stock_move AS sm ON sm.production_id = mp.id AND sm.product_id = mp.product_id
                       JOIN stock_move_line AS sml ON sml.move_id = sm.id
                       JOIN stock_production_lot AS spl ON sml.lot_id = spl.id
                 WHERE pt.tracking IN ('serial', 'lot')
                       AND mp.state IN ('progress', 'to_close', 'done')
                       AND sm.state != 'cancel'
                       AND sml.qty_done > 0
            ),
            mo_to_backorder AS (
                SELECT mo_id
                  FROM mo_id_lot_id
              GROUP BY mo_id
                HAVING COUNT(DISTINCT lot_id) > 1
            )
            SELECT mo_id_lot_id.mo_id AS mo_id,
                   mo_id_lot_id.lot_id AS lot_id,
                   SUM(sml.qty_done / uom_line.factor * uom_mp.factor) AS product_qty,
                   ROW_NUMBER() OVER (PARTITION BY mo_id_lot_id.mo_id) AS backorder_sequence
              INTO TEMPORARY temp_mo_backorder_info
              FROM mo_id_lot_id
                   JOIN mo_to_backorder ON mo_to_backorder.mo_id = mo_id_lot_id.mo_id
                   JOIN stock_move AS sm ON sm.production_id = mo_id_lot_id.mo_id
                   JOIN stock_move_line AS sml ON sml.move_id = sm.id AND mo_id_lot_id.lot_id = sml.lot_id
                   LEFT JOIN uom_uom AS uom_line ON sml.product_uom_id = uom_line.id
                   LEFT JOIN uom_uom AS uom_mp ON mo_id_lot_id.mo_uom_id = uom_mp.id
             WHERE sm.state != 'cancel'
          GROUP BY mo_id_lot_id.mo_id, mo_id_lot_id.lot_id
        """
        )
    if not util.table_exists(cr, "temp_mrp_consumed_line"):
        # (2.) temp_mrp_consumed_line will contains consumed line for each (mo_id, lot_id)
        _logger.info("Create consumed line temporary table")
        cr.execute(
            """
            SELECT b_info.mo_id AS old_mo_id,
                   b_info.lot_id AS lot_id,
                   sm.id AS move_id,
                   sml.id AS consumed_line_id,
                   sml.qty_done AS qty_done
              INTO TEMPORARY temp_mrp_consumed_line
              FROM temp_mo_backorder_info AS b_info
                   JOIN stock_move AS sm ON sm.raw_material_production_id = b_info.mo_id
                   JOIN stock_move_line AS sml ON sml.move_id = sm.id
                   JOIN stock_move_line_stock_production_lot_rel AS rel
                        ON (rel.stock_production_lot_id = b_info.lot_id AND sml.id = rel.stock_move_line_id)
             WHERE sm.state != 'cancel'
            """
        )
    cr.execute("DROP TABLE stock_move_line_stock_production_lot_rel")

    # (3.) Update the MO source and create backorder related too
    _logger.info("Create the backorder MO + update source MO")
    cr.execute("""SELECT max(id) FROM mrp_production""")
    max_id = cr.fetchall()[0]

    cr.execute(
        """
        WITH insert_backorder_production AS (
            INSERT INTO mrp_production
                        ({column_production}, old_id, backorder_sequence,
                        lot_producing_id, name, product_qty, qty_producing)
            SELECT {column_production_pre}, b_info.mo_id,
                   b_info.backorder_sequence, b_info.lot_id,
                   mp.name ||
                           ('-' || REPEAT('0', 2 - TRUNC(LOG(b_info.backorder_sequence))::INT)
                           || b_info.backorder_sequence) AS name,
                   b_info.product_qty, b_info.product_qty
              FROM temp_mo_backorder_info AS b_info
                   JOIN mrp_production AS mp ON mp.id = b_info.mo_id
             WHERE b_info.backorder_sequence != 1
         RETURNING id, old_id, lot_producing_id, product_id, product_qty
        ),
        update_source_mo AS (
            UPDATE mrp_production AS mp
               SET lot_producing_id = b_info.lot_id,
                   name = name ||
                               ('-' || REPEAT('0', 2 - TRUNC(LOG(b_info.backorder_sequence))::INT)
                               || b_info.backorder_sequence),
                   backorder_sequence = b_info.backorder_sequence,
                   product_qty = b_info.product_qty,
                   qty_producing = b_info.product_qty
              FROM temp_mo_backorder_info AS b_info
             WHERE mp.id = b_info.mo_id AND b_info.backorder_sequence = 1
         RETURNING id
        )
        SELECT id FROM insert_backorder_production
         UNION
        SELECT id FROM update_source_mo
    """.format(
            column_production=", ".join(column_production),
            column_production_pre=", ".join(column_production_pre),
        )
    )
    ids_mo = [mo_id for mo_id, in cr.fetchall()]

    # (4.) Create stock move for the backorder mo and update these on MO source
    _logger.info("Create stock move for the backorder MO + update stock move of the MO source")
    cr.execute(
        """
        WITH group_consumed_lines AS (
            SELECT old_mo_id, lot_id, move_id, SUM(qty_done) AS qty_done
              FROM temp_mrp_consumed_line
          GROUP BY old_mo_id, lot_id, move_id
        ),
        create_finished_move_for_backorder_production AS (
            INSERT INTO stock_move ({column_stock_move}, production_id, product_uom_qty, old_id)
            SELECT {column_stock_move_pre}, mp.id, b_info.product_qty, sm.id
              FROM temp_mo_backorder_info AS b_info
                   JOIN mrp_production AS mp ON mp.old_id = b_info.mo_id AND mp.lot_producing_id = b_info.lot_id
                   JOIN stock_move AS sm ON sm.production_id = b_info.mo_id AND sm.product_id = mp.product_id
         RETURNING id, old_id, production_id, product_uom_qty
        ),
        create_raw_move_for_backorder_production AS (
            INSERT INTO stock_move ({column_stock_move}, raw_material_production_id, product_uom_qty, old_id)
            SELECT {column_stock_move_pre}, mp.id, gcl.qty_done, sm.id
              FROM temp_mo_backorder_info AS b_info
                   JOIN mrp_production AS mp ON mp.old_id = b_info.mo_id AND mp.lot_producing_id = b_info.lot_id
                   JOIN stock_move AS sm ON sm.raw_material_production_id = b_info.mo_id
                   JOIN group_consumed_lines AS gcl
                        ON sm.id = gcl.move_id AND gcl.old_mo_id = mp.old_id AND mp.lot_producing_id = gcl.lot_id
         RETURNING id, old_id, raw_material_production_id AS production_id, product_uom_qty
        ),
        new_move AS (
            SELECT * FROM create_raw_move_for_backorder_production
             UNION
            SELECT * FROM create_finished_move_for_backorder_production
        ),
        create_stock_move_m2m AS (
            INSERT INTO stock_move_move_rel (move_orig_id, move_dest_id)
            SELECT new_move.id AS move_orig_id, rel.move_dest_id AS move_dest_id
              FROM stock_move_move_rel AS rel
                   JOIN new_move ON (rel.move_orig_id = new_move.old_id)
             UNION
            SELECT rel.move_orig_id AS move_orig_id, new_move.id AS move_dest_id
              FROM stock_move_move_rel AS rel
                   JOIN new_move ON (rel.move_dest_id = new_move.old_id)
        ),
        qty_remove_by_move AS (
            SELECT old_id AS move_id, SUM(product_uom_qty) AS qty
              FROM new_move
          GROUP BY old_id
        )
        UPDATE stock_move
           SET product_uom_qty = product_uom_qty - qty_remove_by_move.qty
          FROM qty_remove_by_move
         WHERE qty_remove_by_move.move_id = stock_move.id
        """.format(
            column_stock_move=", ".join(column_stock_move), column_stock_move_pre=", ".join(column_stock_move_pre)
        )
    )
    # (5.) Relink stock move line to the new move
    _logger.info("Relink stock move line to the new moves")
    cr.execute(
        """
        UPDATE stock_move_line AS sml
           SET move_id = new_move.id
          FROM stock_move AS new_move
               JOIN temp_mrp_consumed_line ON temp_mrp_consumed_line.move_id = new_move.old_id
               JOIN mrp_production AS new_mo
                    ON new_mo.id = new_move.raw_material_production_id
                       AND new_mo.lot_producing_id = temp_mrp_consumed_line.lot_id
         WHERE new_move.old_id IS NOT NULL
               AND new_mo.old_id IS NOT NULL
               AND sml.id = temp_mrp_consumed_line.consumed_line_id;

        UPDATE stock_move_line AS sml
           SET move_id = new_move.id
          FROM stock_move AS new_move
               JOIN mrp_production AS new_mo ON new_mo.id = new_move.production_id
         WHERE new_move.old_id IS NOT NULL
               AND new_mo.old_id IS NOT NULL
               AND sml.lot_id = new_mo.lot_producing_id
               AND sml.move_id = new_move.old_id
        """
    )

    _logger.info("Clean and recompute some fields")
    if ids_mo:
        # Delete empty move coming from split in (4.)
        util.parallel_execute(
            cr,
            [
                cr.mogrify(
                    """
                    DELETE FROM stock_move
                     WHERE product_uom_qty = 0.0
                       AND (raw_material_production_id IN %(ids)s OR production_id IN %(ids)s)
                    """,
                    {"ids": chunk},
                ).decode()
                for chunk in util.chunks(ids_mo, 100, fmt=tuple)
            ],
        )
    # Clean working column, temporary table and invalidate cache for model used
    util.remove_column(cr, "mrp_production", "old_id")
    util.remove_column(cr, "stock_move", "old_id")
    cr.execute(
        """
        DROP TABLE IF EXISTS temp_mo_backorder_info CASCADE;
        DROP TABLE IF EXISTS temp_mrp_consumed_line CASCADE;
        """
    )

    env["mrp.production"].invalidate_cache()
    env["stock.move"].invalidate_cache()
    env["stock.move.line"].invalidate_cache()

    if ids_mo:
        cr.execute(
            """
               SELECT id
                 FROM stock_move
                WHERE stock_move.raw_material_production_id IN %(ids)s OR stock_move.production_id IN %(ids)s
            """,
            {"ids": tuple(ids_mo)},
        )
        ids_move = [move_id for move_id, in cr.fetchall()]

        inconsistencies.verify_uoms(cr, "mrp.production", uom_field="product_uom_id", ids=ids_mo)
        util.recompute_fields(cr, "mrp.production", ["product_uom_qty"], ids=ids_mo)

        inconsistencies.verify_uoms(cr, "stock.move", uom_field="product_uom", ids=ids_move)
        util.recompute_fields(cr, "stock.move", ["product_qty"], ids=ids_move)

    # Before workorders were created with plan button, now it is done with the bom onchange, then simulate it when needed.
    cr.commit()
    cr.execute(
        """
           SELECT p.id
             FROM mrp_production p
        LEFT JOIN mrp_workorder o
               ON o.production_id = p.id
            WHERE p.state IN ('draft', 'confirmed')
              AND p.bom_id IS NOT NULL
              AND o.id IS NULL
        """
    )

    if not ODOO_UPG_14_PARALLEL_WORKORDER_CREATION:
        if cr.rowcount > 100000:
            _logger.warning(
                "Creating workorders for %d mrp.production, which takes a long time. "
                "This can be sped up by setting the env variable ODOO_UPG_14_PARALLEL_WORKORDER_CREATION to 1. "
                "If you do, be sure to examine the results carefully.",
                cr.rowcount,
            )
        util.iter_browse(
            env["mrp.production"], [r[0] for r in cr.fetchall()], chunk_size=10000, strategy="commit"
        )._create_workorder()
    else:
        # use two-staged chunking to avoid MemoryError in parent by executor.map's eager future creation
        num_task = util.get_max_workers() * 100
        task_size = 1000
        chunk_size = task_size * num_task
        chunks = util.log_progress(
            itertools.takewhile(bool, ([r[0] for r in cr.fetchmany(chunk_size)] for _ in itertools.repeat(None))),
            logger=_logger,
            qualifier=f"mrp.production[:{chunk_size}]",
            size=math.ceil(cr.rowcount / chunk_size),
            log_hundred_percent=True,
        )
        callback = util.make_pickleable_callback(_create_workorder_cb)
        callback.dbname = cr.dbname
        with ProcessPoolExecutor(max_workers=util.get_max_workers()) as executor:
            for chunk in chunks:
                collections.deque(executor.map(callback, util.chunks(chunk, task_size, fmt=tuple)), maxlen=0)
        cr.commit()

    # Recompute fields of stock_move where the compute method changed (only for then linked to a MO)
    ncr = util.named_cursor(cr)
    ncr.execute("SELECT id FROM stock_move WHERE raw_material_production_id IS NOT NULL OR production_id IS NOT NULL")
    chunk = ncr.fetchmany(100000)  # avoid getting millions of ids
    while chunk:
        util.recompute_fields(
            cr,
            "stock.move",
            ["unit_factor", "reference"],
            ids=[r for r, in chunk],
            strategy="commit",
        )
        chunk = ncr.fetchmany(100000)
    ncr.close()

    # Recompute store fields of mrp.production where the compute method changed
    cr.execute("SELECT id FROM mrp_production WHERE state != 'cancel' AND id <= %s", [max_id])
    recompute_state_ids = [id for id, in cr.fetchall()]
    util.recompute_fields(cr, "mrp.production", ["state"], ids=recompute_state_ids, strategy="commit")
    util.recompute_fields(cr, "mrp.production", ["production_location_id"], strategy="commit")

    # New field consumption of workorder is the same than his MO
    cr.execute(
        """
        UPDATE mrp_workorder AS mw
           SET consumption = mp.consumption, product_id = mp.product_id
          FROM mrp_production AS mp
         WHERE mw.production_id = mp.id
        """
    )

    util.remove_column(cr, "mrp_workorder", "finished_lot_id")
    util.remove_column(cr, "mrp_workorder", "qty_producing")  # from former mrp.abstract.workorder parent model
