# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mail_message", "is_internal", "boolean")
    # on next-ob2:
    # parallel queries in 2 pass: ~44 minutes
    # one sequential query: ~41 minutes (looks more io-bound that cpu-bound)
    # parallel queries in 1 pass (current code): ~27 minutes
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
               UPDATE mail_message m
                  SET is_internal = EXISTS (SELECT 1
                                              FROM mail_message_subtype s
                                             WHERE s.id = m.subtype_id
                                               AND s.internal=true)
                WHERE m.is_internal IS NULL
                  AND {parallel_filter}
            """,
            table="mail_message",
            prefix="m.",
        ),
    )

    cr.execute("ALTER TABLE mail_tracking_value RENAME COLUMN field TO _field")
    util.create_column(cr, "mail_tracking_value", "field", "int4")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
                UPDATE mail_tracking_value t
                   SET field = f.id
                  FROM mail_message m, ir_model_fields f
                 WHERE t.mail_message_id = m.id
                   AND f.name = t._field
                   AND m.model = f.model
            """,
            prefix="t.",
        ),
    )

    util.remove_column(cr, "mail_tracking_value", "_field")
    cr.execute("CREATE INDEX ON mail_tracking_value(field)")
    cr.execute("DELETE FROM mail_tracking_value WHERE field IS NULL")

    util.rename_field(cr, "res.company", "catchall", "catchall_email")
    util.remove_model(cr, "email_template.preview")  # easier than renaming + remove extra columns

    util.remove_record(cr, "mail.access_mail_thread_all")

    util.rename_xmlid(cr, "mail.view_message_form", "mail.mail_message_view_form")
