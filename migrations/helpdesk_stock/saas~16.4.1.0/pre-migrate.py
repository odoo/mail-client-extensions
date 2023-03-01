# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_stock.helpdesk_sla_report_analysis_view_search_inherit_sale")
    util.remove_view(cr, "helpdesk_stock.helpdesk_ticket_report_analysis_view_search_inherit_stock")
