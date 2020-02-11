# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mail_message", "is_internal", "boolean")
    cr.execute("""
        UPDATE mail_message m
           SET is_internal = s.internal
          FROM mail_message_subtype s
         WHERE s.id = m.subtype_id
           AND m.is_internal IS NULL
    """)
    cr.execute("UPDATE mail_message SET is_internal = false WHERE is_internal IS NULL")

    cr.execute("ALTER TABLE mail_tracking_value RENAME COLUMN field TO _field")
    util.create_column(cr, "mail_tracking_value", "field", "int4")
    cr.execute("""
        UPDATE mail_tracking_value t
           SET field = f.id
          FROM mail_message m, ir_model_fields f
         WHERE t.mail_message_id = m.id
           AND f.name = t._field
           AND m.model = f.model
    """)
    util.remove_column(cr, "mail_tracking_value", "_field")
    cr.execute("CREATE INDEX ON mail_tracking_value(field)")
    cr.execute("DELETE FROM mail_tracking_value WHERE field IS NULL")

    util.rename_field(cr, "res.company", "catchall", "catchall_email")
    util.remove_model(cr, "email_template.preview")  # easier than renaming + remove extra columns

    util.remove_record(cr, "mail.access_mail_thread_all")

    util.rename_xmlid(cr, "mail.view_message_form", "mail.mail_message_view_form")
