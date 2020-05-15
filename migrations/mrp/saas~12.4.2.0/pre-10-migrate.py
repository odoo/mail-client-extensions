# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "mrp.abstract.workorder", "final_lot_id", "finished_lot_id")
    # The `mrp.abstract.workorder` model only appears in saas~12.2
    # For prior versions, we should be explicit.
    util.rename_field(cr, "mrp.workorder", "final_lot_id", "finished_lot_id")
    util.rename_field(cr, "mrp.product.produce", "final_lot_id", "finished_lot_id")

    util.rename_field(cr, "mrp.production", "propagate", "propagate_cancel")
    util.create_column(cr, "mrp_production", "propagate_date", "boolean")
    util.create_column(cr, "mrp_production", "propagate_date_minimum_delta", "int4")

    cr.execute("UPDATE mrp_production SET propagate_date_minimum_delta = 1, propagate_date = true")

    util.create_m2m(
        cr,
        "mrp_workcenter_alternative_rel",
        "mrp_workcenter",
        "mrp_workcenter",
        "workcenter_id",
        "alternative_workcenter_id",
    )

    # replace date_planned_(start|finished) by a resource leave (leave_id) on workorder
    util.create_column(cr, "mrp_workorder", "leave_id", "int4")
    cr.execute(
        """
        WITH _leaves AS (
            INSERT INTO resource_calendar_leaves (name, date_from, date_to, resource_id)
                SELECT o.id::varchar, o.date_planned_start, o.date_planned_finished, c.resource_id
                  FROM mrp_workorder o
                  JOIN mrp_workcenter c ON c.id = o.workcenter_id
                 WHERE o.date_planned_start IS NOT NULL
                   AND o.date_planned_finished IS NOT NULL

            RETURNING id, name::int4 AS wo_id
        )
        UPDATE mrp_workorder w
           SET leave_id = l.id
          FROM _leaves l
         WHERE l.wo_id = w.id
        ;

        UPDATE resource_calendar_leaves
           SET name = NULL
         WHERE id IN (SELECT leave_id FROM mrp_workorder)
    """
    )

    util.remove_column(cr, "mrp_workorder", "date_planned_start")
    util.remove_column(cr, "mrp_workorder", "date_planned_finished")

    util.remove_field(cr, "mrp.bom.line", "valid_product_attribute_value_wnva_ids")
