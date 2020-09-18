# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_act_window
           SET binding_model_id = NULL
         WHERE id=%s
    """, [util.ref(cr, 'calendar_sms.calendar_event_act_window_sms_composer_single')])
