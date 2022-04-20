# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
        INSERT INTO mrp_workorder_dependencies_rel(workorder_id, blocked_by_id)
             SELECT next_work_order_id, id
               FROM mrp_workorder
              WHERE next_work_order_id IS NOT NULL
        """
    )
    util.remove_field(cr, "mrp.workorder", "next_work_order_id")
