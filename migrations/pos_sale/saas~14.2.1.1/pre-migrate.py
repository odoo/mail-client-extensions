# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "pos_sale.crm_team_salesteams_view_kanban_inherit_pos_sale", "pos_sale.crm_team_view_kanban_dashboard"
    )
