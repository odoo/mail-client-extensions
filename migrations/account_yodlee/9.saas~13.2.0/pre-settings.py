# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    fields = util.splitlines("""
        service_url
        id
        secret
        user_login
        user_password
        new_user_login
        new_user_password
        new_user_email
    """)
    for f in fields:
        util.remove_field(cr, 'account.config.settings', 'yodlee_' + f)

    util.remove_field(cr, 'res.company', 'yodlee_last_login')
    util.remove_field(cr, 'res.company', 'yodlee_user_last_login')
