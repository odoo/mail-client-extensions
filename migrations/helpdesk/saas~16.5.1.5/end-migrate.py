# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    xmlids = [
        ("helpdesk.mt_ticket_refund_posted", "helpdesk.mt_ticket_refund_status"),
        ("helpdesk.mt_ticket_refund_cancel", "helpdesk.mt_ticket_refund_status"),
        ("helpdesk.mt_ticket_return_done", "helpdesk.mt_ticket_return_status"),
        ("helpdesk.mt_ticket_return_cancel", "helpdesk.mt_ticket_return_status"),
        ("helpdesk.mt_ticket_repair_done", "helpdesk.mt_ticket_repair_status"),
        ("helpdesk.mt_ticket_repair_cancel", "helpdesk.mt_ticket_repair_status"),
    ]
    subtypes = {util.ref(cr, old): util.ref(cr, new) for old, new in xmlids}
    util.replace_record_references_batch(cr, subtypes, "mail.message.subtype", replace_xmlid=False)

    subtype_to_remove = [
        "mt_ticket_refund_posted",
        "mt_ticket_refund_cancel",
        "mt_ticket_return_done",
        "mt_ticket_return_cancel",
        "mt_ticket_repair_done",
        "mt_ticket_repair_cancel",
        "mt_team_ticket_stage",
        "mt_team_ticket_refund_posted",
        "mt_team_ticket_refund_cancel",
        "mt_team_ticket_return_done",
        "mt_team_ticket_return_cancel",
        "mt_team_ticket_repair_done",
        "mt_team_ticket_repair_cancel",
    ]
    for sub_type in subtype_to_remove:
        util.remove_record(cr, f"helpdesk.{sub_type}")
