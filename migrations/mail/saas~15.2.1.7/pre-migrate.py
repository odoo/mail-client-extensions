# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.message", "add_sign", "email_add_signature")
    util.rename_field(cr, "mail.compose.message", "add_sign", "email_add_signature")
    util.update_field_references(cr, "layout", "email_layout_xmlid", only_models=("mail.compose.message",))
    util.remove_field(cr, "mail.compose.message", "layout")

    # Deduplicate notifications
    cr.execute(
        """
     DELETE
       FROM mail_notification
      WHERE id IN (
         SELECT UNNEST((ARRAY_AGG(id ORDER BY coalesce(is_read, false) desc, id desc))[2:])
           FROM mail_notification
       GROUP BY res_partner_id, mail_message_id, notification_type
          )
        """
    )

    # remove lost activities to add a constraint
    cr.execute("DELETE FROM mail_activity WHERE res_id = 0")
