# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'crm.team', 'team_type')
    util.remove_field(cr, 'crm.team', 'dashboard_graph_type')
    util.remove_field(cr, 'crm.team', 'dashboard_graph_model')
    util.remove_field(cr, 'crm.team', 'dashboard_graph_group')
    util.remove_field(cr, 'crm.team', 'dashboard_graph_period')

    util.remove_view(cr, "sales_team.crm_team_view_form")
