# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, xml_id='sales_team.view_sale_config_settings')

    cr.execute("""
        UPDATE ir_ui_view SET type = 'sales_team_dashboard'
        WHERE id = %s
        """,
        [util.ref(cr, 'sales_team.crm_team_salesteams_view_kanban')])

