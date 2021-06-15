# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "mrp.workorder", "move_line_id", "workorder_line_id")
    util.rename_field(cr, "quality.check", "move_line_id", "workorder_line_id")
    util.rename_field(cr, "quality.check", "final_lot_id", "finished_lot_id")

    util.remove_view(cr, "mrp_workorder.mrp_routing_workcenter_view_form_inherit_workorder")

    util.create_column(cr, "res_config_settings", "group_mrp_wo_tablet_timer", "boolean")

    cr.execute(
        """
        UPDATE quality_check qc
           SET workorder_line_id = wl.id,
               lot_id = wl.lot_id,
               qty_done = wl.qty_to_consume,
               component_id = m.product_id,
               production_id = mp.id
          FROM mrp_workorder_line wl
          JOIN stock_move m ON m.id = wl.move_id
          JOIN product_product p on p.id = m.product_id
          JOIN product_template pt on pt.id = p.product_tmpl_id,
               mrp_production mp
         WHERE qc.workorder_id = CASE
                 WHEN (m.raw_material_production_id IS NOT NULL AND m.production_id IS NULL) THEN wl.raw_workorder_id
                 ELSE wl.finished_workorder_id
               END
           AND qc.point_id IS NULL
           AND m.state not in ('done', 'cancel')
           AND NOT pt.tracking = 'none'
           AND qc.workorder_line_id IS NULL
           AND qc.component_id IS NOT NULL
    """
    )
