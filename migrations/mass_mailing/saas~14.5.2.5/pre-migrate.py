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
    util.update_field_usage(cr, "mailing.trace", "scheduled", "create_date")
    util.update_field_usage(cr, "mailing.trace", "state_update", "write_date")

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

    util.rename_field(cr, "mailing.mailing", "unique_ab_testing", "ab_testing_enabled")
    util.rename_field(cr, "mailing.mailing", "contact_ab_pc", "ab_testing_pc")
    util.create_column(cr, "mailing_mailing", "ab_testing_completed", "boolean")
    util.create_column(cr, "utm_campaign", "ab_testing_winner_selection", "varchar", default="opened_ratio")
    util.create_column(cr, "utm_campaign", "ab_testing_schedule_datetime", "timestamp without time zone")
    util.create_column(cr, "utm_campaign", "ab_testing_completed", "boolean")
    util.create_column(cr, "utm_campaign", "ab_testing_total_pc", "integer", default=0)
    cr.execute(
        """
        WITH ab_test_mailing AS (
            SELECT
                campaign_id,
                SUM(ab_testing_pc) AS total_pc
            FROM mailing_mailing
            WHERE ab_testing_enabled IS TRUE
            GROUP BY campaign_id
        )
        UPDATE utm_campaign
        SET ab_testing_total_pc = ab_test_mailing.total_pc
        FROM ab_test_mailing
        WHERE ab_test_mailing.campaign_id = utm_campaign.id
    """
    )
    cr.execute(
        """
            UPDATE mailing_mailing
               SET ab_testing_pc = GREATEST(LEAST(COALESCE(ab_testing_pc, 0), 100), 0),
                   body_arch = body_html
        """
    )
