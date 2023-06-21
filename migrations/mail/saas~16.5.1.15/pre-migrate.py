# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
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
