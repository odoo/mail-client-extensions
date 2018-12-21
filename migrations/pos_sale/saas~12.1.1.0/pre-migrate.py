# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, 'pos_sale.pos_sales_team')
    util.remove_field(cr, 'crm.team', 'team_type')
    util.remove_field(cr, 'crm.team', 'dashboard_graph_group_pos')
    util.remove_record(cr, 'pos_sale.crm_team_view_form_inherit_pos_sale')
