# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # remove views
    util.remove_view(cr, "event_sms.event_mail_view_tree")
    util.remove_view(cr, "event_sms.event_mail_view_form")
    util.remove_view(cr, "event_sms.event_event_view_form_inherit_sms")
    util.remove_view(cr, "event_sms.event_type_view_form")

    # move the M2O field `template_id` to the new reference field `template_ref`
    for table_name in ["event_mail", "event_type_mail"]:
        # Remove inconsistent records from the database
        cr.execute(
            f"""
        DELETE FROM {table_name}
              WHERE notification_type = 'sms'
                AND sms_template_id IS NULL
         """,
        )

        cr.execute(
            f"""
        UPDATE {table_name}
           SET template_ref = CONCAT('sms.template,', sms_template_id)
         WHERE notification_type = 'sms'
         """,
        )
        model_name = util.model_of_table(cr, table_name)
        util.remove_field(cr, model_name, "sms_template_id")
