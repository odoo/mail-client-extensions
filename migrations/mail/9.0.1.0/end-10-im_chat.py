# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, 'im_chat_message'):
        return

    env = util.env(cr)
    Channels = env['mail.channel'].with_context(dict(tz='UTC'))

    public_user = env.ref('base.public_user').partner_id.id
    subtype_id = util.ref(cr, 'mail.mt_comment')

    cr.execute("""
        SELECT s.id, s.uuid, string_agg(p.name, ', ')
          FROM im_chat_session s
          JOIN im_chat_session_res_users_rel r ON (s.id = r.session_id)
          JOIN res_users u ON (u.id = r.user_id)
          JOIN res_partner p ON (p.id = u.partner_id)
         WHERE EXISTS(SELECT id FROM im_chat_message m WHERE m.to_id = s.id)
      GROUP BY s.id, s.uuid
    """)
    for sid, uuid, name in cr.fetchall():
        # easier to use ORM to create alias correctly
        chan = Channels.create({
            'name': name,
            'channel_type': 'chat',
            'uuid': uuid,
            'email_send': False,
            'public': 'private',
            'group_public_id': False,
        })

        cr.execute("""
            INSERT INTO mail_channel_partner(partner_id, channel_id, fold_state,
                                             is_minimized, is_pinned)
                 SELECT u.partner_id, %s, r.state, true, true
                        FROM im_chat_session_res_users_rel r
                        JOIN res_users u ON (u.id = r.user_id)
                       WHERE session_id=%s
                   """, [chan.id, sid])

        cr.execute("""
            INSERT INTO mail_message(
                model, res_id, author_id, body, message_type, subtype_id, create_date, date
            )
            SELECT 'mail.channel', %s, COALESCE(u.partner_id, %s), m.message, 'comment', %s,
                   m.create_date, m.create_date
              FROM im_chat_message m
         LEFT JOIN res_users u ON (u.id = m.from_id)
             WHERE m.type = 'message'
               AND m.to_id = %s
          ORDER BY m.create_date ASC
        """, [chan.id, public_user, subtype_id, sid])

    cr.execute("DROP TABLE im_chat_message")
    cr.execute("DROP TABLE im_chat_session_res_users_rel")
    cr.execute("DROP TABLE im_chat_session")
