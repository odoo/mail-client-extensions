# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    user = util.ref(cr, "base.group_user")
    portal = util.ref(cr, "base.group_portal")
    public = util.ref(cr, "base.group_public")
    settings = util.ref(cr, "base.group_system")
    accessrights = util.ref(cr, "base.group_erp_manager")
    usability = util.ref(cr, "base.module_category_usability")

    u2id = util.ENVIRON["user2_id"]
    assert isinstance(u2id, int)

    # remove public users from all other non usability groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid != %(public)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id = %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(public)s)
                AND uid NOT IN (1, %(u2id)s)
    """, locals())

    # remove portal users from all other non usability group
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid != %(portal)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id = %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(portal)s)
                AND uid NOT IN (1, %(u2id)s)
    """, locals())

    # remove SUPERUSER and user2 from `portal` and `public` groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid IN (%(portal)s, %(public)s)
                AND uid IN (1, %(u2id)s)
    """, locals())
    # and force them to `employee`, `settings` and `access rights` groups
    util.fixup_m2m(cr, 'res_groups_users_rel', 'res_users', 'res_groups', 'uid', 'gid')
    cr.execute("""
        INSERT INTO res_groups_users_rel(uid, gid)
             VALUES (1, %(user)s), (%(u2id)s, %(user)s)
                  , (1, %(settings)s), (%(u2id)s, %(settings)s)
                  , (1, %(accessrights)s), (%(u2id)s, %(accessrights)s)
        ON CONFLICT DO NOTHING
    """, locals())
