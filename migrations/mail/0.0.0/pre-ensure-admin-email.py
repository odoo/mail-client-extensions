# -*- coding: utf-8 -*-
try:
    from odoo.tools import email_split

    from odoo.addons.base.maintenance.migrations import util
except ImportError:
    from openerp.tools import email_split

    from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    if not env.user.email:
        if email_split(env.user.login):
            cr.execute(
                """
                    UPDATE res_partner rp
                       SET email = ru.login
                      FROM res_users ru
                     WHERE ru.id = %s
                       AND ru.partner_id = rp.id
                """,
                [env.user.id],
            )
        else:
            cr.execute("SELECT value FROM ir_config_parameter WHERE key = 'mail.catchall.domain'")
            [domain] = cr.fetchone()
            cr.execute(
                """
                   UPDATE mail_alias ma
                      SET alias_name = COALESCE(ma.alias_name, ru.login)
                     FROM res_users ru
                    WHERE ru.id = %s
                      AND ru.alias_id = ma.id
                RETURNING ma.alias_name
                """,
                [env.user.id],
            )
            [username] = cr.fetchone()
            email = "{username}@{domain}".format(username=username, domain=domain)
            cr.execute(
                """
                    UPDATE res_partner rp
                       SET email = %s
                      FROM res_users ru
                     WHERE ru.id = %s
                       AND ru.partner_id = rp.id
                """,
                [email, env.user.id],
            )
