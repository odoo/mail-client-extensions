# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "project_id", "int4")
    cr.execute("""
        UPDATE product_template
           SET service_tracking='task_in_project'
         WHERE service_tracking='task_new_project'
    """)
