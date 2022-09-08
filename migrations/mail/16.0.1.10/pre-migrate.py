# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.email_message_tree_view")

    # The following templates layout have been renamed:
    # mail.message_notification_email --> mail.mail_notification_layout
    # mail.mail_notification_paynow --> mail.mail_notification_layout_with_responsible_signature
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """UPDATE mail_message
                  SET email_layout_xmlid = 'mail.mail_notification_layout'
                WHERE email_layout_xmlid = 'mail.message_notification_email'""",
            table="mail_message",
        )
        + util.explode_query_range(
            cr,
            """UPDATE mail_message
                  SET email_layout_xmlid = 'mail.mail_notification_layout_with_responsible_signature'
                WHERE email_layout_xmlid = 'mail.mail_notification_paynow'""",
            table="mail_message",
        ),
    )
    util.remove_view(cr, "mail.mail_notification_paynow")
    util.remove_view(cr, "mail.message_notification_email")

    util.remove_field(cr, "mail.render.mixin", "model_object_field")
    util.remove_field(cr, "mail.render.mixin", "sub_object")
    util.remove_field(cr, "mail.render.mixin", "sub_model_object_field")
    util.remove_field(cr, "mail.render.mixin", "null_value")
    util.remove_field(cr, "mail.render.mixin", "copyvalue")

    util.change_field_selection_values(
        cr,
        "ir.actions.server",
        "state",
        {"email": "mail_post"},
    )
    util.create_column(cr, "ir_act_server", "mail_post_autofollow", "boolean")
    util.create_column(cr, "ir_act_server", "mail_post_method", "varchar")
    cr.execute(
        """
            UPDATE ir_act_server
               SET mail_post_method = 'email'
             WHERE state = 'mail_post'
        """
    )

    char_to_dt = """
        create function char_to_dt(text) returns timestamp as $$
        begin
            return $1::timestamp;
        exception when others then
            return NULL;
        end;
        $$ LANGUAGE plpgsql IMMUTABLE RETURNS NULL ON NULL INPUT PARALLEL SAFE;
    """
    cr.execute(char_to_dt)
    cr.execute(
        """
        ALTER TABLE mail_mail
       ALTER COLUMN scheduled_date TYPE timestamp
              USING char_to_dt(scheduled_date)
    """
    )
    cr.execute("DROP FUNCTION char_to_dt(text)")

    query = """
        UPDATE mail_channel
           SET channel_type = 'group', group_public_id = NULL
         WHERE channel_type = 'channel'
           AND public = 'private'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="mail_channel"))
    util.update_record_from_xml(cr, "mail.mail_channel_rule")
    util.update_record_from_xml(cr, "mail.ir_rule_mail_channel_member_group_user")
    util.remove_field(cr, "mail.channel", "public")
