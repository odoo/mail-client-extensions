# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # log when having both phone and mobile, then merge, then remove mobile
    cr.execute(
        """
            INSERT INTO mail_message (author_id, body, date, message_type, model, res_id, subtype_id)
                 SELECT %(root_id)s as author_id,
                        concat('Mobile number ',
                               reg.mobile,
                               ' removed in favor of phone number') as body,
                        now() at time zone 'utc' as date,
                        'notification' as message_type,
                        'event.registration' AS model,
                        reg.id as res_id,
                        %(note_id)s as subtype_id
                   FROM event_registration AS reg
                  WHERE reg.phone IS NOT NULL AND
                        reg.mobile IS NOT NULL AND
                        reg.phone != reg.mobile
        """,
        {"root_id": util.ref(cr, "base.partner_root"), "note_id": util.ref(cr, "mail.mt_note")},
    )
    cr.execute(
        """
            UPDATE event_registration
               SET phone = mobile
             WHERE phone IS NULL and mobile IS NOT NULL
        """
    )
    util.remove_field(cr, "event.registration", "mobile")
