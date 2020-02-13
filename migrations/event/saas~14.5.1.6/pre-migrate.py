# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "use_ticket")
    util.remove_field(cr, "event.type", "use_mail_schedule")
    util.remove_field(cr, "event.type", "use_timezone")
    util.create_column(cr, "event_type", "note", "text")

    # move the M2O field `template_id` to the new reference field `template_ref`
    for table_name in ["event_mail", "event_type_mail"]:
        # Remove inconsistent records from the database
        cr.execute(
            f"""
        DELETE FROM {table_name}
              WHERE notification_type = 'mail'
                AND template_id IS NULL
         """,
        )

        util.create_column(cr, table_name, "template_ref", "varchar")

        cr.execute(
            f"""
        UPDATE {table_name}
           SET template_ref = CONCAT('mail.template,', template_id)
         WHERE notification_type = 'mail'
         """,
        )
        model_name = util.model_of_table(cr, table_name)
        util.remove_field(cr, model_name, "template_id")
