# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "mrp_workorder_line", "is_finished"):
        cr.execute("""
            UPDATE mrp_workorder_line
               SET finished_workorder_id = raw_workorder_id,
                   raw_workorder_id = NULL
             WHERE is_finished = true
        """)
        util.remove_field(cr, "mrp.workorder.line", "is_finished")
