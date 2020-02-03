# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "order_line_id", "int4")

    cr.execute("""
        UPDATE planning_slot s
           SET order_line_id = t.sale_line_id
          FROM project_task t
         WHERE t.id = s.task_id
    """)
