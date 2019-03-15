# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mrp_production", "date_planned_start_wo", "timestamp without time zone")
    util.create_column(cr, "mrp_production", "date_planned_finished_wo", "timestamp without time zone")
    util.create_column(cr, "mrp_production", "date_start_wo", "timestamp without time zone")
    util.create_column(cr, "mrp_production", "orderpoint_id", "int4")

    cr.execute(
        """
        WITH dates AS (
            SELECT production_id,
                   (array_agg(date_planned_start ORDER BY date_planned_start NULLS LAST))[1] started,
                   (array_agg(date_planned_finished ORDER BY date_planned_finished NULLS LAST))[1] finished
              FROM mrp_workorder
          GROUP BY production_id
        )
        UPDATE mrp_production p
           SET date_planned_start_wo = d.started,
               date_planned_finished_wo = d.finished
          FROM dates d
         WHERE d.production_id = p.id
    """  # noqa
    )

    util.remove_field(cr, "mrp.workorder", "active_move_line_ids")
    util.remove_field(cr, "stock.move.line", "done_wo")
    util.remove_field(cr, "stock.move", "active_move_line_ids")

    cr.execute("DELETE FROM mrp_product_produce_line")  # TransientModel
    cr.execute("DELETE FROM mrp_product_produce")  # TransientModel
    util.remove_column(cr, "mrp_product_produce", "product_id")
    util.rename_field(cr, "mrp.product.produce", "product_qty", "qty_producing")
    util.rename_field(cr, "mrp.product.produce", "lot_id", "final_lot_id")
    util.rename_field(cr, "mrp.product.produce", "produce_line_ids", "workorder_line_ids")
