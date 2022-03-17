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
         SELECT UNNEST((ARRAY_AGG(id ORDER BY coalesce(is_read, false) desc, notification_type asc, id desc))[2:])
           FROM mail_notification
          WHERE res_partner_id IS NOT NULL
       GROUP BY res_partner_id, mail_message_id
          )
        """
    )

    # remove lost activities to add a constraint
    cr.execute("DELETE FROM mail_activity WHERE res_id = 0")

    util.create_column(cr, "mail_notification", "author_id", "int4")
    query = """
        UPDATE mail_notification n
           SET author_id = m.author_id
          FROM mail_message m
         WHERE n.mail_message_id = m.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="mail_notification", alias="n"))

    # adapt mail templates from method rename in odoo/odoo@a018735ec4cb1c0c230a7599e0fe2a30785878cc
    cr.execute(
        r"""
        UPDATE mail_template
           SET body_html = regexp_replace(body_html,
                                          'object\.with_context\(force_website=True\)\.get_access_action\(\)',
                                          'object._get_access_action(force_website=True)',
                                          'g')
         WHERE body_html like '%get\_access\_action%'
        """
    )
    # and the translations
    cr.execute(
        r"""
        UPDATE ir_translation
           SET value = regexp_replace(value,
                                      'object\.with_context\(force_website=True\)\.get_access_action\(\)',
                                      'object._get_access_action(force_website=True)',
                                      'g')
         WHERE name = 'mail.template,body_html'
           AND value like '%get\_access\_action%'
        """
    )
