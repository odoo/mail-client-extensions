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
    """, [(user, portal), public])

    # remove portal users from `employee` group
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid = %s
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %s)
    """, [user, portal])
