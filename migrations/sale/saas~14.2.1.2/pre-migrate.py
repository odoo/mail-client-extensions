# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "sale.crm_team_salesteams_view_kanban", "sale.crm_team_view_kanban_dashboard")
