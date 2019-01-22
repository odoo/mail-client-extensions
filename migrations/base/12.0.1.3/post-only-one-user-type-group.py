# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    user = util.ref(cr, "base.group_user")
    portal = util.ref(cr, "base.group_portal")
    public = util.ref(cr, "base.group_public")

    # remove public users from `portal` and `employee` groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid IN %s
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %s)
                AND uid != 1
    """, [(user, portal), public])

    # remove portal users from `employee` group
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid = %s
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %s)
                AND uid != 1
    """, [user, portal])

    # remove SUPERUSER from `portal` and `public` groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid IN %s
                AND uid = 1
    """, [(portal, public)])
    # and force it to `employee` group
    cr.execute("""
        INSERT INTO res_groups_users_rel(uid, gid)
             VALUES (1, %s)
        ON CONFLICT DO NOTHING
    """, [user])
