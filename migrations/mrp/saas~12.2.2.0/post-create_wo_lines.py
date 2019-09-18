# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    wo = "raw_workorder_id" if util.version_gte("saas~12.3") else "workorder_id"
    cr.execute("""
        INSERT INTO mrp_workorder_line(id, {}, move_id, product_id, product_uom_id, lot_id,
                                       qty_to_consume, qty_reserved, qty_done)

        SELECT id, workorder_id, move_id, product_id, product_uom_id, lot_id,
               product_qty, product_uom_qty, qty_done
          FROM stock_move_line
         WHERE workorder_id IS NOT NULL
           AND done_wo = true
    """.format(wo))

    cr.execute("SELECT COALESCE(max(id), 0) + 1 FROM mrp_workorder_line")
    cr.execute("ALTER SEQUENCE mrp_workorder_line_id_seq RESTART WITH %s", cr.fetchone())

    # now flag finished wo_lines
    if util.column_exists(cr, "mrp_workorder_line", "is_finished"):
        # saas-12.2 only
        cr.execute("""
            UPDATE mrp_workorder_line l
               SET is_finished = true
              FROM stock_move m
             WHERE m.id = l.move_id
               AND m.raw_material_production_id IS NULL
               AND m.production_id IS NOT NULL
        """)
    else:
        # >= saas-12.3
        cr.execute("""
            UPDATE mrp_workorder_line l
               SET finished_workorder_id = l.raw_workorder_id,
                   raw_workorder_id = NULL
              FROM stock_move m
             WHERE m.id = l.move_id
               AND m.raw_material_production_id IS NULL
               AND m.production_id IS NOT NULL
        """)

    util.remove_field(cr, "stock.move.line", "done_wo")
