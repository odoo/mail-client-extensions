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
