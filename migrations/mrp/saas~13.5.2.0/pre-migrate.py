# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mrp.mrp_production_workorder_form_view_inherit_gantt")
    # remove mail.thread and mail.activity.mixin inheritance
    util.remove_inherit_from_model(cr, 'mrp.workorder', 'mail.thread')
    util.remove_inherit_from_model(cr, 'mrp.workorder', 'mail.activity.mixin')

    cr.execute(
        """
    UPDATE mrp_production
       SET priority = CASE WHEN priority IN ('2', '3')
                           THEN '1'
                           ELSE '0'
                      END
     WHERE priority IN ('1', '2', '3') OR priority IS NULL
        """
    )

    cr.execute(
        """
    UPDATE stock_move AS sm
       SET priority = mp.priority
      FROM mrp_production AS mp
     WHERE sm.raw_material_production_id = mp.id
        """
    )

    util.remove_field(cr, "mrp.production", "delay_alert")
    util.remove_field(cr, "mrp.production", "propagate_date")
    util.remove_field(cr, "mrp.production", "propagate_date_minimum_delta")
