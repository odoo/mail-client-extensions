# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'base.config.settings', *eb('{default_,}mail_push_notification'))

    renames = util.splitlines("""
        mail_push.{default_,}mail_push_notification
        {,mail_push.}fcm_api_key
        {,mail_push.}fcm_project_id
    """)
    for r in renames:
        from_, to = eb(r)
        cr.execute("UPDATE ir_config_parameter SET key=%s WHERE key=%s", [to, from_])
