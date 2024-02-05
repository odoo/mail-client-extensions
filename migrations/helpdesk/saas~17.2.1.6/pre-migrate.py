# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    old = util.ref(cr, "helpdesk.mail_act_helpdesk_handle")
    new = util.ref(cr, "mail.mail_activity_data_todo")

    util.replace_record_references_batch(cr, {old: new}, "mail.activity.type", replace_xmlid=False)
    util.remove_record(cr, "helpdesk.mail_act_helpdesk_handle")

    cr.execute("DROP VIEW IF EXISTS helpdesk_sla_report_analysis")
    cr.execute("DROP VIEW IF EXISTS helpdesk_ticket_report_analysis")
    util.alter_column_type(cr, "helpdesk_ticket", "assign_hours", "float8")
    util.alter_column_type(cr, "helpdesk_ticket", "close_hours", "float8")
