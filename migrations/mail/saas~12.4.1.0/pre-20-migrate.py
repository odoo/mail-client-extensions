# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # util.rename_model(cr, "mail.blacklist.mixin", "mail.thread.blacklist")
    util.rename_field(cr, "mail.message", "layout", "email_layout_xmlid")
    util.rename_field(cr, "mail.tracking.value", "groups", "field_groups")

    # `mail.compose.message` is loosing its inheritance from `mail.message`
    # remove extra fields
    gone = """
        date
        child_ids
        author_avatar
        needaction_partner_ids
        needaction
        has_error
        channel_ids
        notification_ids
        starred_partner_ids
        starred
        tracking_value_ids
        message_id      # "Message-Id" in mails
        moderation_status
        moderator_id
        need_moderation

        # inheritance from `rating` module
        rating_ids
        rating_value

        # from `snailmail` module
        snailmail_error
        snailmail_status
        letter_ids

        # from `website_mail` module
        description
        website_published
    """

    for field in util.splitlines(gone):
        util.remove_field(cr, "mail.compose.message", field)
