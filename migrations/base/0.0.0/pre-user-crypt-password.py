# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~11.4"):
        _password_crypt(cr)


def _password_crypt(cr):
    if not util.version_gte("saas~12.1") and util.module_installed(cr, "auth_crypt"):
        cr.execute("UPDATE res_users SET password_crypt=password WHERE password_crypt IS NULL AND password IS NOT NULL")
        util.remove_column(cr, "res_users", "password")
        cr.execute("ALTER TABLE res_users RENAME COLUMN password_crypt TO password")
        util.remove_field(cr, "res.users", "password_crypt")

    # Encrypting hundred of thousands passwords takes times. Delay the encryption after upgrade for such a case.
    cr.execute(
        r"""
            SELECT count(*) FROM res_users
             WHERE password IS NOT NULL
               AND password !~ '^\$[^$]+\$[^$]+\$.'
        """
    )
    (to_crypt_passwords,) = cr.fetchone()
    if to_crypt_passwords > 10000:
        cr.execute("ALTER TABLE res_users RENAME COLUMN password TO _upg_password_to_crypt")
        util.create_column(cr, "res_users", "password", "varchar")
