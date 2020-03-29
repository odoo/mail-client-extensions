# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_forecast", "order_line_id", "int4")

    cr.execute("""
        UPDATE project_forecast s
           SET order_line_id = t.sale_line_id
          FROM project_task t
         WHERE t.id = s.task_id
    """)
