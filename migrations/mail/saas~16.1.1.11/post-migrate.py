# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    group_id = util.ref(cr, "mail.group_mail_notification_type_inbox")
    cr.execute(
        """
            INSERT INTO res_groups_users_rel(gid, uid)
                 SELECT %s, id FROM res_users WHERE notification_type = 'inbox'
        """,
        [group_id],
    )
