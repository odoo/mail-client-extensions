# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    if util.column_exists(cr, "mail_message", "website_published"):
        # from website_mail, see odoo/odoo@5649fc88e8f3022f4143400a124f2e3c1e5c0df8
        # NOTE uses `is not true` instead of `not` to handle NULL values
        adapter = lambda leaf, _, __: [(leaf[0], leaf[1], not leaf[2])]
        if util.column_exists(cr, "mail_message", "is_internal"):
            util.update_field_references(
                cr,
                "website_published",
                "is_internal",
                only_models=("mail.message",),
                domain_adapter=adapter
            )
            util.parallel_execute(
                cr,
                util.explode_query(
                    cr,
                    "UPDATE mail_message SET is_internal = (website_published is not true) WHERE is_internal IS NULL",
                ),
            )
            util.remove_field(cr, "mail.message", "website_published")
        else:
            util.move_field_to_module(cr, "mail.message", "website_published", "website_mail", "mail")
            util.rename_field(
                cr, "mail.message", "website_published", "is_internal", domain_adapter=adapter
            )
            # XXX took ~15 minutes with `ALTER TABLE`
            #          ~60 minutes with `UPDATE`
            #          ~30 minutes with parallized `UPDATE` (8 workers, 100k bucket)
            cr.execute("ALTER TABLE mail_message ALTER COLUMN is_internal TYPE boolean USING (is_internal is not true)")

    else:
        util.create_column(cr, "mail_message", "is_internal", "boolean", default=True)

    cr.execute("ALTER TABLE mail_tracking_value RENAME COLUMN field TO _field")
    util.create_column(cr, "mail_tracking_value", "field", "int4")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE mail_tracking_value t
                   SET field = f.id
                  FROM mail_tracking_value mtv
                  JOIN mail_message m ON mtv.mail_message_id = m.id
                  JOIN ir_model_fields f ON f.name = mtv._field AND m.model = f.model
                 WHERE t.id=mtv.id
            """,
            table="mail_tracking_value",
            bucket_size=250_000,
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
