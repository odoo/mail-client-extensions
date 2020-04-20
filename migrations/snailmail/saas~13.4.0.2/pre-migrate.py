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
            notification_status,
            failure_type,
            failure_reason
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
            END,
            CASE
                WHEN l.state = 'error' THEN
                    CASE
                        WHEN l.error_code = 'CREDIT_ERROR' THEN 'sn_credit'
                        WHEN l.error_code = 'TRIAL_ERROR' THEN 'sn_trial'
                        WHEN l.error_code = 'NO_PRICE_AVAILABLE' THEN 'sn_price'
                        WHEN l.error_code = 'MISSING_REQUIRED_FIELDS' THEN 'sn_fields'
                        WHEN l.error_code = 'FORMAT_ERROR' THEN 'sn_format'
                        ELSE 'sn_error'
                    END
                ELSE NULL
            END,
            CASE
                WHEN l.state = 'error' THEN l.info_msg
                ELSE NULL
            END
        FROM snailmail_letter l
        WHERE NOT EXISTS(SELECT 1 FROM mail_message_res_partner_needaction_rel WHERE letter_id = l.id)
    """
    )
