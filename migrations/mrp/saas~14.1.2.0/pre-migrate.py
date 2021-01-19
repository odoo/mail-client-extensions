# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "workorder_done_count")
    # is_planned become stored. This fills the computed values the first time
    util.create_column(cr, "mrp_production", "is_planned", "boolean", default=False)

    # production.is_planned = any(wo.date_planned_start and wo.date_planned_finished for wo in production.workorder_ids)
    cr.execute(
        """
        WITH planned AS (
            SELECT production_id AS id
              FROM mrp_workorder
             WHERE date_planned_start IS NOT NULL
               AND date_planned_finished IS NOT NULL
          GROUP BY production_id
        )
     UPDATE mrp_production mo
        SET is_planned = true
       FROM planned
      WHERE mo.id = planned.id
        """
    )

    util.remove_field(cr, "mrp.workorder", "use_create_components_lots")
