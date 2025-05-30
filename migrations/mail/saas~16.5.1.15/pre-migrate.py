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

    util.remove_constraint(cr, "mail_alias", "mail_alias_alias_unique")

    cr.execute(
        """
            CREATE TABLE mail_alias_domain (
                id SERIAL NOT NULL PRIMARY KEY,
                name varchar,
                bounce_alias varchar,
                catchall_alias varchar,
                default_from varchar
            );
        """
    )
    util.create_column(
        cr, "mail_message", "record_alias_domain_id", "int4", fk_table="mail_alias_domain", on_delete_action="SET NULL"
    )
    util.create_column(
        cr, "mail_message", "record_company_id", "int4", fk_table="res_company", on_delete_action="SET NULL"
    )
    # ... as well as composer update to support those (and skip computes)
    util.create_column(
        cr,
        "mail_compose_message",
        "record_alias_domain_id",
        "int4",
        fk_table="mail_alias_domain",
        on_delete_action="SET NULL",
    )
    util.create_column(
        cr, "mail_compose_message", "record_company_id", "int4", fk_table="res_company", on_delete_action="SET NULL"
    )

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
        "icp_mail_default_from",
    ]:
        util.rename_xmlid(cr, f"base.{xml_id}", f"mail.{xml_id}", on_collision="merge")

    # prepare column to store alias domain from ICP
    util.create_column(
        cr, "res_company", "alias_domain_id", "int4", fk_table="mail_alias_domain", on_delete_action="SET NULL"
    )

    # create alias domain table to migrate config parameters
    cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'mail.catchall.domain'")
    res = cr.fetchone()
    alias_domain = res[0] if res else False
    alias_domain_id = False
    if alias_domain:
        cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'mail.bounce.alias'")
        res = cr.fetchone()
        bounce_alias = res[0] if res else "bounce"
        cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'mail.catchall.alias'")
        res = cr.fetchone()
        catchall_alias = res[0] if res else "catchall"
        cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'mail.default.from'")
        res = cr.fetchone()
        default_from = res[0] if res else ""

        cr.execute(
            """
                INSERT INTO mail_alias_domain (name, bounce_alias, catchall_alias, default_from)
                     VALUES (%s, %s, %s, %s)
                  RETURNING id
            """,
            (alias_domain, bounce_alias, catchall_alias, default_from),
        )
        [alias_domain_id] = cr.fetchone()
        cr.execute(
            """
                UPDATE res_company
                   SET alias_domain_id = %s
            """,
            (alias_domain_id,),
        )
        # warn admins
        util.add_to_migration_reports(
            f"""
<details>
<summary>
    The alias domain {alias_domain} has been migrated into a full model called
    'Alias Domain'. It is now setup to be used by default in all companies.
    Incoming email alias check is still done only based on left-part of alias
    email address. You can now choose a stricter check based on full email
    by unchecking 'Local-part based incoming detection' parameter on aliases.
</summary>
<ul>
    <li>Multiple domains are now supported, allowing more fine grain tuning
    of reply-to, catchall, ...</li>
    <li>Stricter email address check now performed on incoming emails, allowing
    to have same alias_name with different domain</li>
    <li>Odoo does not support configuration parameters anymore</li>
</ul>
</details>
            """,
            category="Mail",
            format="html",
        )

    # alias domains configuration update
    util.remove_field(cr, "res.config.settings", "alias_domain")

    # migrate aliases: set domain (if configured), set gateway check based on
    # left-part only, to be backward compatible and ease transition
    util.create_column(
        cr, "mail_alias", "alias_domain_id", "int4", fk_table="mail_alias_domain", on_delete_action="SET NULL"
    )
    util.create_column(cr, "mail_alias", "alias_incoming_local", "boolean", default=True)
    if alias_domain_id:
        cr.execute(
            """
                UPDATE mail_alias aliases
                   SET alias_domain_id = %s
            """,
            (alias_domain_id,),
        )
    # remove alias_user_id; will remove from inherits also (see alias mixins)
    util.remove_field(cr, "mail.alias", "alias_user_id")

    # finally remove useless ICP
    util.remove_record(cr, "mail.icp_mail_bounce_alias")
    util.remove_record(cr, "mail.icp_mail_catchall_alias")
    util.remove_record(cr, "mail.icp_mail_default_from")

    # activities
    util.create_column(cr, "mail_activity", "active", "boolean", default=True)
    util.create_column(cr, "mail_activity", "date_done", "date")

    # archive livechat with public users since guest should be used now
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
