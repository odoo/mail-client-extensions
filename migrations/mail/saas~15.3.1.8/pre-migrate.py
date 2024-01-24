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

    util.remove_model(cr, "mail.resend.cancel", drop_table=True)

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
          WITH subquery AS (
        SELECT cp.id,
               MAX(m.id) as max_id
          FROM mail_channel_partner as cp
          JOIN mail_message as m ON m.model = 'mail.channel'
           AND cp.channel_id = m.res_id
           AND m.author_id = cp.partner_id
         WHERE {parallel_filter}
      GROUP BY cp.id
        HAVING cp.seen_message_id < MAX(m.id) OR cp.seen_message_id IS NULL
        )
        UPDATE mail_channel_partner
           SET seen_message_id = subquery.max_id
          FROM subquery
         WHERE mail_channel_partner.id = subquery.id
            """,
            table="mail_channel_partner",
            alias="cp",
        ),
    )
