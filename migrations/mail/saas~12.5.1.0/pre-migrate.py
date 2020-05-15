# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_message_res_partner_needaction_rel", "notification_type", "varchar")
    util.create_column(cr, "mail_message_res_partner_needaction_rel", "read_date", "timestamp without time zone")

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE mail_message_res_partner_needaction_rel
                   SET notification_type = CASE WHEN is_email THEN 'email' ELSE 'inbox' END
                 WHERE notification_type IS NULL
                   AND {parallel_filter}
            """,
        ),
    )

    util.remove_field(cr, "mail.notification", "is_email")
    util.rename_field(cr, "mail.notification", "email_status", "notification_status")

    util.rename_field(cr, "mail.message", "needaction_partner_ids", "notified_partner_ids")

    util.remove_view(cr, "mail.qunit_mobile_suite")

    # Function `format_tz` has been renamed to `format_datetime`.
    # Key word argument `format` has been renamed to `dt_format`.
    # `mail_template` and `ir_translation` records must be updated.
    cr.execute(r"""
        UPDATE ir_translation
           SET src = regexp_replace(
                       regexp_replace(src,
                                      '(?:\yformat_tz)(\(.*?)(?:,\s*format\s*=)(.*?(?=\)))',
                                      'format_datetime\1, dt_format=\2',
                                      'g'),
                       '\yformat_tz\y',
                       'format_datetime',
                       'g'),
               value = regexp_replace(
                         regexp_replace(value,
                                        '(?:\yformat_tz)(\(.*?)(?:,\s*format\s*=)(.*?(?=\)))',
                                        'format_datetime\1, dt_format=\2',
                                        'g'),
                         '\yformat_tz\y',
                         'format_datetime',
                         'g')
         WHERE name = 'mail.template,body_html'
           AND src ~ '\yformat_tz\y'
            OR value ~ '\yformat_tz\y'
    """)

    cr.execute(r"""
        UPDATE mail_template
           SET body_html = regexp_replace(
                             regexp_replace(body_html,
                                            '(?:\yformat_tz)(\(.*?)(?:,\s*format\s*=)(.*?(?=\)))',
                                            'format_datetime\1, dt_format=\2',
                                            'g'),
                             '\yformat_tz\y',
                             'format_datetime',
                             'g')
         WHERE body_html ~ '\yformat_tz\y'
    """)
