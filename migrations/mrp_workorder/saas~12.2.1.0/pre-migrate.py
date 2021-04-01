# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "quality.check", "lot_id", "final_lot_id")

    util.remove_view(cr, "mrp_workorder.mrp_production_view_form_inherit_planning")

    # cleanup non-done wo on quality checks
    cr.execute(
        """
        UPDATE quality_check c
           SET move_line_id = NULL
          FROM (
                   SELECT qc.id
                     FROM quality_check qc
                LEFT JOIN mrp_workorder_line l ON qc.move_line_id = l.id
                    WHERE l.id IS NULL
               ) as to_update
         WHERE c.id = to_update.id
    """
    )
