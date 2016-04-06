# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    task_activity_id = util.ref(cr, 'crm.crm_activity_data_meeting')
    cr.execute("""
        UPDATE crm_lead
           SET next_activity_id = %s
         WHERE next_activity_id IS NULL
           AND (title_action IS NOT NULL OR date_action IS NOT NULL)
    """, [task_activity_id])
