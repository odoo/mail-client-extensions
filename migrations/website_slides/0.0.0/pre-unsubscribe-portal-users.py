# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("15.0", "17.0"):
        discussion = util.ref(cr, "mail.mt_comment")
        cr.execute(
            """
            DELETE FROM mail_followers_mail_message_subtype_rel r
             USING mail_followers f,
                   res_users u
             WHERE u.partner_id = f.partner_id
               AND r.mail_followers_id = f.id
               AND r.mail_message_subtype_id = %s
               AND f.res_model = 'slide.channel'
               AND u.share = true
            """,
            [discussion],
        )
