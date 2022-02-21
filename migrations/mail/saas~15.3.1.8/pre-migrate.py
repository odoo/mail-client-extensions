# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.thread", "message_unread")
    util.remove_field(cr, "mail.thread", "message_unread_counter")

    cr.execute(
        """
            UPDATE mail_channel
               SET group_public_id = NULL
             WHERE channel_type != 'channel'
        """
    )

    cr.execute(
        """
            DELETE FROM mail_channel_res_groups_rel mcrg
                  USING mail_channel c
                  WHERE mcrg.mail_channel_id = c.id
                    AND c.channel_type != 'channel'
        """
    )
