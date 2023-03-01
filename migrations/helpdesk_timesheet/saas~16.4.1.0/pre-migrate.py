# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_sla_report_analysis_view_search_timesheet")
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_ticket_report_analysis_view_search_timesheet")
