# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/enterprise/pull/26832
    util.if_unchanged(cr, "helpdesk.helpdesk_portal_ticket_rule", util.update_record_from_xml)
    # https://github.com/odoo/enterprise/pull/31804
    util.if_unchanged(cr, "helpdesk.helpdesk_sla_report_analysis_rule_manager", util.update_record_from_xml)
