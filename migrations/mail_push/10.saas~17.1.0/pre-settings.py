# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, 'base.config.settings', *eb('{default_,}mail_push_notification'))
    cr.execute("""
        UPDATE ir_config_parameter
           SET key='mail_push.mail_push_notification'
         WHERE key='mail_push.default_mail_push_notification'
    """)
