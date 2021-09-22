# -*- coding: utf-8 -*-

from odoo.upgrade import util
from odoo.upgrade.util.jinja_to_qweb import upgrade_jinja_fields


def migrate(cr, version):
    # Drop the old table of the many2many on the <mail.channel>
    cr.execute("DROP TABLE mail_channel_moderator_rel CASCADE")

    # Remove models
    util.remove_model(cr, "mail.moderation")

    # Remove the <mail.channel> that was inserted into the <mail.group> table
    cr.execute(
        """
        DELETE FROM mail_channel
              WHERE email_send = True
        """
    )

    # Remove field <res.users>
    util.remove_field(cr, "res.users", "is_moderator")
    util.remove_field(cr, "res.users", "moderation_counter")
    util.remove_field(cr, "res.users", "moderation_channel_ids")

    # Remove fields <mail.channel>
    util.remove_field(cr, "mail.channel", "email_send")
    util.remove_field(cr, "mail.channel", "moderation")
    util.remove_field(cr, "mail.channel", "moderator_ids")
    util.remove_field(cr, "mail.channel", "moderation_notify")
    util.remove_field(cr, "mail.channel", "moderation_notify_msg")
    util.remove_field(cr, "mail.channel", "moderation_guidelines")
    util.remove_field(cr, "mail.channel", "moderation_guidelines_msg")

    util.remove_field(cr, "mail.channel", "is_moderator")
    util.remove_field(cr, "mail.channel", "moderation_ids")
    util.remove_field(cr, "mail.channel", "moderation_count")

    # Remove field <mail.message>
    util.remove_field(cr, "mail.message", "need_moderation")
    util.remove_field(cr, "mail.message", "moderator_id")
    util.remove_field(cr, "mail.message", "moderation_status")

    # Remove views
    util.remove_view(cr, "mail.mail_channel_send_guidelines")
    util.remove_view(cr, "mail.mail_channel_notify_moderation")

    # Remove records
    util.remove_record(cr, "mail.ir_cron_mail_notify_channel_moderators")
    util.remove_record(cr, "mail.mail_moderation_rule_user")

    inline_template_fields = [
        "subject",
        "email_from",
        "email_to",
        "partner_to",
        "email_cc",
        "reply_to",
        "report_name",
        "scheduled_date",
    ]
    qweb_fields = ["body_html"]

    upgrade_jinja_fields(cr, "mail_template", inline_template_fields, qweb_fields)
