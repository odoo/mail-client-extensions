# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "is_partially_planned")
    # is_planned become stored. This fills the computed values the first time
    util.create_column(cr, "mrp_production", "is_planned", "boolean")
    cr.execute(
        """
     UPDATE mrp_production mo
        SET is_planned = wo.date_planned_start IS NOT NULL and wo.date_planned_finished IS NOT NULL
       FROM mrp_workorder wo
      WHERE wo.production_id = mo.id
        """
    )
    util.remove_field(cr, "mrp.production", "workorder_done_count")
    util.remove_field(cr, "mrp.workorder", "use_create_components_lots")
