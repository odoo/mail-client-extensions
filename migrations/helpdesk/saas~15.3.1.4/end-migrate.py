# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "helpdesk.helpdesk_ticket_report_analysis_rule_user")
