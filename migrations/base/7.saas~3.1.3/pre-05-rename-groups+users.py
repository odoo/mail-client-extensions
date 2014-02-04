# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    groups = {
        'portal.group_anonymous': 'base.group_public',
        'portal.group_portal': 'base.group_portal',
        'portal_anonymous.anonymous_user': 'base.public_user',
        'portal_anonymous.anonymous_user_res_partner': 'base.public_partner',
    }

    for old, new in groups.items():
        old_module, _, old_name = old.partition('.')
        new_module, _, new_name = new.partition('.')

        cr.execute("""UPDATE ir_model_data
                         SET noupdate=%s,
                             module=%s,
                             name=%s
                       WHERE module=%s
                         AND name=%s
                   """, (False, new_module, new_name, old_module, old_name))

    todel = [
        'portal_anonymous.anonymous_user_mail_alias',
    ]

    for old in todel:
        old_module, _, old_name = old.partition('.')
        cr.execute("""DELETE FROM ir_model_data
                            WHERE module=%s
                              AND name=%s
                   """, (old_module, old_name))

    util.remove_module(cr, 'portal_anonymous')
