# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_status")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "sla_name")
    subtype_to_update = [
        "mt_ticket_rated",
        "mt_ticket_refund_posted",
        "mt_ticket_refund_cancel",
        "mt_ticket_return_done",
        "mt_ticket_return_cancel",
        "mt_ticket_repair_done",
        "mt_ticket_repair_cancel",
        "mt_team_ticket_new",
        "mt_team_ticket_refund_posted",
        "mt_team_ticket_refund_cancel",
        "mt_team_ticket_return_done",
        "mt_team_ticket_return_cancel",
        "mt_team_ticket_repair_done",
        "mt_team_ticket_repair_cancel",
    ]
    for sub_type in subtype_to_update:
        util.if_unchanged(cr, f"helpdesk.{sub_type}", util.update_record_from_xml)
