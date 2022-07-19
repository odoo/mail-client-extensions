# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.email_message_tree_view")

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
