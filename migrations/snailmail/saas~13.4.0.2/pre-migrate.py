# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.message", "snailmail_status")
    util.remove_field(cr, "mail.mail", "snailmail_status")

    util.create_column(cr, "mail_message_res_partner_needaction_rel", "letter_id", "int4")

    cr.execute(
        """
        INSERT INTO mail_message_res_partner_needaction_rel(
            mail_message_id,
            res_partner_id,
            notification_type,
            letter_id,
            is_read,
            notification_status
        )
        SELECT
            l.message_id,
            l.partner_id,
            'snail',
            l.id,
            true,
            CASE
                WHEN l.state = 'pending' THEN 'ready'
                WHEN l.state = 'sent' THEN 'sent'
                WHEN l.state = 'error' THEN 'exception'
                WHEN l.state = 'canceled' THEN 'cancelled'
            END
        FROM snailmail_letter l
        WHERE NOT EXISTS(SELECT 1 FROM mail_message_res_partner_needaction_rel WHERE letter_id = l.id)
    """
    )
