# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_act_window
           SET binding_model_id = NULL
         WHERE id=%s
    """, [util.ref(cr, 'project_forecast.action_project_task_view_planning')])
