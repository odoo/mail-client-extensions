# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.team", "customer_satisfaction")
    cr.execute("ALTER TABLE res_users ALTER COLUMN helpdesk_target_closed TYPE int4")

    util.rename_field(cr, "helpdesk.sla.report.analysis", "sla_status_failed", "sla_status_fail")

    util.remove_field(cr, "helpdesk.sla.report.analysis", "sla_exceeded_days")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "sla_id")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_open_hours")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_failed")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_fold")
    util.remove_field(cr, "helpdesk.sla.status", "exceeded_days")

    util.create_column(cr, "helpdesk_sla_status", "exceeded_hours", "float8")
    util.create_column(cr, "helpdesk_ticket", "sla_reached", "boolean")

    # https://github.com/odoo/enterprise/pull/26811
    util.if_unchanged(cr, "helpdesk.helpdesk_portal_ticket_rule", util.update_record_from_xml)
