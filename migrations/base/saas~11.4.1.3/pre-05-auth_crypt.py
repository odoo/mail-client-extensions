# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, 'auth_crypt'):
        return
    cr.execute("UPDATE res_users SET password = password_crypt WHERE password_crypt IS NOT NULL")
