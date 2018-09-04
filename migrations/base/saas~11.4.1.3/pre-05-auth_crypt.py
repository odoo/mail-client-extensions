# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, 'auth_crypt'):
        return
    cr.execute("UPDATE res_users SET password_crypt=password WHERE password_crypt IS NULL AND password IS NOT NULL")
    util.remove_column(cr, "res_users", "password")
    cr.execute("ALTER TABLE res_users RENAME COLUMN password_crypt TO password")
    util.remove_field(cr, "res.users", "password_crypt")
