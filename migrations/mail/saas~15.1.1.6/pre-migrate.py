# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.mail_notification_borders")

    util.rename_field(cr, "mail.resend.message", "has_cancel", "can_cancel")

    # Non-internal users can not receive notification in Odoo (only by email)
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE res_users
           SET notification_type = 'email'
         WHERE share = TRUE
           AND notification_type != 'email'
           """,
            table="res_users",
        ),
    )

    # constraint mail_channel_partner_partner_unique fails for multiple saas-15.1 DBs
    # coming from the same template
    util.ensure_xmlid_match_record(
        cr,
        "mail.channel_partner_general_channel_for_admin",
        "mail.channel.partner",
        {
            "partner_id": util.ref(cr, "base.partner_admin"),
            "channel_id": util.ref(cr, "mail.channel_all_employees"),
        },
    )
