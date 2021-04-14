# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DELETE FROM mailing_trace WHERE model IS NULL OR res_id IS NULL")

    util.rename_field(cr, "mailing.mailing", "ignored", "canceled")
    # trace status refactoring
    util.rename_field(cr, "mailing.trace", "clicked", "links_click_datetime")
    util.rename_field(cr, "mailing.trace", "opened", "open_datetime")
    util.rename_field(cr, "mailing.trace", "replied", "reply_datetime")
    util.rename_field(cr, "mailing.trace", "sent", "sent_datetime")
    util.rename_field(cr, "mailing.trace", "state", "trace_status")
    util.update_field_references(cr, "scheduled", "create_date", only_models=("mailing.trace",))
    util.update_field_references(cr, "state_update", "write_date", only_models=("mailing.trace",))

    util.change_field_selection_values(
        cr,
        "mailing.trace",
        "failure_type",
        {"SMTP": "mail_smtp", "RECIPIENT": "mail_email_invalid", "UNKNOWN": "unknown", "BOUNCE": "unknown"},
    )
    util.change_field_selection_values(
        cr,
        "mailing.trace",
        "trace_status",
        {"replied": "reply", "opened": "open", "bounced": "bounce", "exception": "error", "ignored": "cancel"},
    )

    util.remove_field(cr, "mailing.trace", "bounced")
    util.remove_field(cr, "mailing.trace", "exception")
    util.remove_field(cr, "mailing.trace", "ignored")
    util.remove_field(cr, "mailing.trace", "scheduled")
    util.remove_field(cr, "mailing.trace", "state_update")
