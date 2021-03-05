# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mail.activity", "force_next")
    util.remove_field(cr, "mail.activity.type", "force_next")

    util.rename_field(cr, "mail.activity.type", "default_next_type_id", "triggered_next_type_id")
    util.rename_field(cr, "mail.activity.type", "next_type_ids", "suggested_next_type_ids")
    util.rename_field(cr, "mail.activity.type", "default_description", "default_note")

    util.create_column(cr, "mail_activity_type", "chaining_type", "varchar")

    cr.execute(
        """UPDATE mail_activity_type
           SET chaining_type = CASE WHEN triggered_next_type_id IS NOT NULL
                                    THEN 'trigger'
                                    ELSE 'suggest'
                               END"""
    )

    cr.execute(
        """
        ALTER TABLE mail_message_res_partner_needaction_rel
          RENAME TO mail_notification
    """
    )
    cr.execute(
        """
        ALTER SEQUENCE mail_message_res_partner_needaction_rel_id_seq
             RENAME TO mail_notification_id_seq
    """
    )
