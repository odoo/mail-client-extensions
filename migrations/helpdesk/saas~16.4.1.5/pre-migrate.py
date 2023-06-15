# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "helpdesk.sla.report.analysis", "sla_status_fail", "sla_fail")
    util.rename_field(cr, "helpdesk.sla.report.analysis", "ticket_stage_id", "stage_id")
    util.rename_field(cr, "helpdesk.ticket.report.analysis", "ticket_stage_id", "stage_id")
    for field in [
        "ticket_deadline",
        "sla_reached_datetime",
        "sla_status_successful",
        "sla_status_ongoing",
    ]:
        util.remove_field(cr, "helpdesk.sla.report.analysis", field)
    util.remove_view(cr, "helpdesk.helpdesk_ticket_view_graph_7days_analysis_inherit_dashboard")
    util.remove_record(cr, "helpdesk.helpdesk_ticket_action_7days_analysis")
    util.remove_record(cr, "helpdesk.helpdesk_ticket_action_7days_analysis_pivot")
    util.remove_record(cr, "helpdesk.helpdesk_ticket_action_7days_analysis_graph")
