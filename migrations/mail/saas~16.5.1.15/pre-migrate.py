# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "mail_tracking_value", "fields_info", "text")

    # move *_monetary values into *_float, as they are the same type in DB
    util.explode_execute(
        cr,
        """
            UPDATE mail_tracking_value
               SET old_value_float = old_value_monetary,
                   new_value_float = new_value_monetary
             WHERE field_type = 'monetary'
        """,
        table="mail_tracking_value",
    )
    util.rename_field(cr, "mail.tracking.value", "field", "field_id")
    util.remove_field(cr, "mail.tracking.value", "field_desc")
    util.remove_field(cr, "mail.tracking.value", "field_type")
    util.remove_field(cr, "mail.tracking.value", "old_value_monetary")
    util.remove_field(cr, "mail.tracking.value", "new_value_monetary")
    util.remove_field(cr, "mail.tracking.value", "tracking_sequence")

    # mail.message model update
    util.remove_field(cr, "mail.message", "canned_response_ids")
    util.remove_field(cr, "mail.shortcode", "message_ids")

    # alias views renaming
    for pre, post in [
        ("view_mail_alias_form", "mail_alias_view_form"),
        ("view_mail_alias_tree", "mail_alias_view_tree"),
        ("view_mail_alias_search", "mail_alias_view_search"),
        ("action_view_mail_alias", "mail_alias_action"),
    ]:
        util.rename_xmlid(cr, f"mail.{pre}", f"mail.{post}")

    # ICP move
    for xml_id in [
        "icp_mail_catchall_alias",
        "icp_mail_bounce_alias",
        "icp_mail_default_from",
    ]:
        util.rename_xmlid(cr, f"base.{xml_id}", f"mail.{xml_id}", on_collision="merge")

    public_group_id = util.ref(cr, "base.group_public")
    cr.execute(
        """
        WITH public_partner_ids AS (
            SELECT u.partner_id
              FROM res_users u
              JOIN res_groups_users_rel r
                ON r.uid = u.id
             WHERE r.gid = %s
        )
        DELETE
          FROM discuss_channel_member m
         USING public_partner_ids p
         WHERE p.partner_id = m.partner_id
        """,
        [public_group_id],
    )

    # Web Push Move Enterprise -> Community
    util.move_model(cr, "mail.partner.device", "mail_enterprise", "mail")
    util.move_model(cr, "mail.notification.web.push", "mail_enterprise", "mail")

    cr.execute(
        """
            UPDATE ir_config_parameter
               SET "key" = 'mail.web_push_vapid_private_key'
             WHERE "key" = 'mail_enterprise.web_push_vapid_private_key'
        """
    )
    cr.execute(
        """
            UPDATE ir_config_parameter
               SET "key" = 'mail.web_push_vapid_public_key'
             WHERE "key" = 'mail_enterprise.web_push_vapid_public_key'
        """
    )

    for xml_id in [
        "ir_cron_web_push_notification",
        "ir_cron_web_push_notification_ir_actions_server",
    ]:
        util.rename_xmlid(cr, f"mail_enterprise.{xml_id}", f"mail.{xml_id}", on_collision="merge")

    util.remove_record(cr, "auth_signup.reset_password_email")

    # remove alias_user_id; will remove from inherits also (see alias mixins)
    util.remove_field(cr, "mail.alias", "alias_user_id")

    util.create_column(cr, "mail_activity", "active", "boolean", default=True)
    # channel ACL simplification
    records_to_remove = [
        "mail.discuss_channel_rule",
        "mail.discuss_channel_admin",
        "mail.access_mail_message_scheduled_all",
        "mail.ir_rule_discuss_channel_member_group_user",
        "mail.access_mail_mail_all",
        "mail.access_mail_mail_portal",
        "mail.access_mail_mail_user",
        "mail.access_mail_followers_all",
        "mail.access_discuss_channel_admin",
        "mail.access_discuss_channel_rtc_session_all",
        "mail.access_mail_alias_all",
        "mail.access_mail_message_reaction_all",
        "mail.access_mail_tracking_value_all",
        "mail.access_mail_tracking_value_portal",
        "mail.access_mail_tracking_value_user",
        "mail.access_mail_activity_all",
        "mail.access_mail_activity_plan_all",
        "mail.access_mail_activity_plan_template_all",
        "mail.access_mail_activity_schedule_all",
        "mail.access_mail_activity_type_all",
        "mail.access_mail_guest_all",
        "mail.access_mail_ice_server_all",
        "mail.access_res_users_settings_volumes_all",
    ]
    for name in records_to_remove:
        util.remove_record(cr, name)
