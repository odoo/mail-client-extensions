# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    _group_public = {
        'name': 'Public',
        'comment': 'Public users have specific access rights (such as record rules and restricted menus). \
                    They usually do not belong to the usual OpenERP groups.',
    }

    _user_public = {
        'login': 'public',
        'password': '',
        'active': False,
        # image stay the same
    }

    updates = {
        'portal.group_anonymous': ('base.group_public', _group_public),
        'portal.group_portal': ('base.group_portal', None),
        'portal_anonymous.anonymous_user': ('base.public_user', _user_public),
        'portal_anonymous.anonymous_user_res_partner': ('base.public_partner', dict(name='Public user', active=False)),
    }

    for old, (new, data) in updates.items():
        old_module, _, old_name = old.partition('.')
        new_module, _, new_name = new.partition('.')

        cr.execute("""UPDATE ir_model_data
                         SET noupdate=%s,
                             module=%s,
                             name=%s
                       WHERE module=%s
                         AND name=%s
                   RETURNING model, res_id
                   """, (False, new_module, new_name, old_module, old_name))

        model, res_id = cr.fetchone() or [None, None]
        if not res_id or not data:
            continue
        upd, params = zip(*(('%s=%%s' % k, v) for k, v in data.iteritems()))
        query = 'UPDATE "%s" SET %s WHERE id=%%s' % (util.table_of_model(cr, model), ','.join(upd))
        params = tuple(params) + (res_id,)
        cr.execute(query, params)

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
