# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # update groups here https://github.com/odoo/odoo/pull/39961/files#diff-d5a69b75d883e0ad813c91cde1da0be8R8
    # If we don't do this then all the channels that are not live chats will be hidden for Administrator
    ir_rule_id = util.ref(cr, "mail.mail_channel_rule")
    group_user_id = util.ref(cr, "base.group_user")
    group_portal_id = util.ref(cr, "base.group_portal")
    group_public_id = util.ref(cr, "base.group_public")

    cr.execute(
        """
        INSERT INTO rule_group_rel(rule_group_id, group_id)
            VALUES (%s, %s), (%s, %s), (%s, %s)
        ON CONFLICT DO NOTHING
    """,
        [
            ir_rule_id,
            group_user_id,
            ir_rule_id,
            group_portal_id,
            ir_rule_id,
            group_public_id,
        ],
    )
