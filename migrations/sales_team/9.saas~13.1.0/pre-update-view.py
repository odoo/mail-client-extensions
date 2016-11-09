# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'sales_team.crm_team_salesteams_view_kanban', False)

    cr.execute("""
        UPDATE ir_ui_view SET type = 'kanban'
        WHERE id = %s
        """,
        [util.ref(cr, 'sales_team.crm_team_salesteams_view_kanban')])
