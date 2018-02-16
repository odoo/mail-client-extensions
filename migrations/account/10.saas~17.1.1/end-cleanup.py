# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if version is not None and util.dbuuid(cr) in {'8851207e-1ff9-11e0-a147-001cc0f2115e'}:
        # slow: delayed on odoo database
        return

    cr.execute("DELETE FROM mail_message WHERE model='account.move'")
    cr.execute("DELETE FROM mail_followers WHERE res_model='account.move'")


if __name__ == '__builtin__':
    env = env   # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
