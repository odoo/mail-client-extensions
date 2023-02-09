# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    xmlids = ("helpdesk_ticket_report_analysis_rule_user", "helpdesk_ticket_user_rule", "helpdesk_user_rule")
    for xmlid in xmlids:
        util.update_record_from_xml(cr, f"helpdesk.{xmlid}")
