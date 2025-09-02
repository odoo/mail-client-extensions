# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "res_users", "_upg_password_to_crypt"):
        util.remove_column(cr, "res_users", "password")
        cr.execute("ALTER TABLE res_users RENAME COLUMN _upg_password_to_crypt TO password")

        code = r"""
            env.cr.execute(
                '''
                    SELECT id, password FROM res_users
                     WHERE password IS NOT NULL
                       AND password !~ '^\$[^$]+\$[^$]+\$.'
                     LIMIT 10000
                '''
            )
            if env.cr.rowcount:
                Users = env["res.users"].sudo()
                passwords = env.cr.fetchall()
                n = 100
                for i in range(0, len(passwords), n):
                    for uid, pw in passwords[i:i + n]:
                        Users.browse(uid).write({"password": pw})
                    env.cr.commit()
        """

        util.create_cron(cr, "Encrypt passwords", "res.users", code)
