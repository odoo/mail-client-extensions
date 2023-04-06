# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # activity type management update
    util.remove_field(cr, "mail.activity", "force_next")
    util.remove_field(cr, "mail.activity.type", "force_next")

    util.rename_field(cr, "mail.activity.type", "default_next_type_id", "triggered_next_type_id")
    util.rename_field(cr, "mail.activity.type", "next_type_ids", "suggested_next_type_ids")
    util.rename_field(cr, "mail.activity.type", "default_description", "default_note")

    util.create_column(cr, "mail_activity_type", "chaining_type", "varchar")

    cr.execute(
        """UPDATE mail_activity_type
           SET chaining_type = CASE WHEN triggered_next_type_id IS NOT NULL
                                    THEN 'trigger'
                                    ELSE 'suggest'
                               END"""
    )

    # duplicate field removal
    util.update_field_usage(cr, "mail.message", "is_subscribed", "is_member")
    util.remove_field(cr, "mail.channel", "is_subscribed")

    # remove followers being channels, not supported anymore -> simply remove
    # them as feature is mainly populating channels and not sending real
    # notification; mail.channel now uses its members and do not need any follower
    # migration. We remove followers having partner_id set as NULL to remove
    # both channel followers and potential invalid entries (both NULL)
    cr.execute("DELETE FROM mail_followers WHERE partner_id IS NULL ")
    # also remove followers of channel, as channels now use members only for
    # notification purpose
    cr.execute("DELETE FROM mail_followers WHERE res_model = 'mail.channel'")

    # removal of channel following feature
    util.remove_field(cr, "mail.thread", "message_channel_ids")
    util.remove_field(cr, "mail.wizard.invite", "channel_ids")
    util.remove_field(cr, "mail.followers", "channel_id")
    util.remove_field(cr, "ir.actions.server", "channel_ids")

    # removal of channel listener feature: message are now linked with model / res_id
    # and multi-channel notification is simply dropped out (hence dropping table
    # without remorse)
    util.remove_field(cr, "mail.message", "channel_ids")
    util.remove_field(cr, "mail.channel", "channel_message_ids")

    # constraints to remove: done when column removed, removing from constraint table
    util.remove_constraint(cr, "mail_followers", "mail_followers_res_channel_res_model_id_uniq")
    util.remove_constraint(cr, "mail_followers", "partner_xor_channel")

    # removal of channel listener feature: message are now linked with model / res_id
    # and multi-channel notification is simply dropped out (hence dropping table
    # without remorse)
    cr.execute("""DROP TABLE IF EXISTS mail_message_mail_channel_rel CASCADE""")

    # remove invalid entries as m2m channel/partner table now has partner_id and channel_id required
    cr.execute("DELETE FROM mail_channel_partner WHERE partner_id IS NULL OR channel_id IS NULL")

    # rename mail_message_res_partner_needaction_rel table to mail_notification
    cr.execute(
        """
        ALTER TABLE mail_message_res_partner_needaction_rel
          RENAME TO mail_notification
    """
    )
    cr.execute(
        """
        ALTER SEQUENCE mail_message_res_partner_needaction_rel_id_seq
             RENAME TO mail_notification_id_seq
    """
    )
