# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.notification", "mail_id", "mail_mail_id")
    util.change_field_selection_values(
        cr,
        "mail.notification",
        "failure_type",
        {"SMTP": "mail_smtp", "RECIPIENT": "mail_email_invalid", "UNKNOWN": "unknown", "BOUNCE": "unknown"},
    )
    # create failure type and set failure type to unknown as we do not want to try
    # to compute back failure types in details
    util.create_column(cr, "mail_mail", "failure_type", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr, "UPDATE mail_mail SET failure_type='unknown' WHERE state='exception'", table="mail_mail"
        ),
    )
    util.rename_field(cr, "mail.mail", "notification", "is_notification")

    util.create_column(cr, "mail_activity_type", "res_model", "varchar")
    cr.execute(
        """
        UPDATE mail_activity_type mat
           SET res_model = m.model
          FROM ir_model m
         WHERE m.id = mat.res_model_id
    """
    )

    util.remove_field(cr, "mail.activity.type", "res_model_id")
    util.remove_field(cr, "mail.activity.type", "initial_res_model_id")

    cr.execute(
        """
            DELETE FROM mail_channel_partner WHERE id IN (
                  SELECT unnest((array_agg(id ORDER BY id))[2:])
                    FROM mail_channel_partner
                GROUP BY partner_id, channel_id
                  HAVING count(*) > 1
            )
        """
    )

    util.ensure_xmlid_match_record(
        cr,
        "mail.channel_partner_general_channel_for_admin",
        "mail.channel.partner",
        {
            "partner_id": util.ref(cr, "base.partner_admin"),
            "channel_id": util.ref(cr, "mail.channel_all_employees"),
        },
    )

    # Force the channel "all employees" to stay a mail channel
    # and to not be converted into a mail group
    channel_all_employees = util.ref(cr, "mail.channel_all_employees")
    if channel_all_employees:
        cr.execute(
            """
            UPDATE mail_channel
               SET email_send = FALSE
             WHERE id = %s
            """,
            (channel_all_employees,),
        )

    env = util.env(cr)
    host = env["ir.config_parameter"].get_param("web.base.url")
    util.add_to_migration_reports(
        f"""
        <p><strong>PLEASE NOTE:</strong></p>
        <p>
            Mass mailing channels are no longer displayed in the Discuss app
            by default starting from Odoo 15.0. <br>
            They become mail groups and are moved to <a href="{host}/groups">{host}/groups</a>, where you can
            subscribe and follow discussions. <br>
            If you prefer to keep a channel in the Discuss app after the upgrade, go to the channel
            settings and uncheck the "send messages by email" option.
        </p>
        """,
        "Discuss",
        format="html",
    )
