# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    u2id = util.ENVIRON.get("user2_id")
    assert isinstance(u2id, int)
    one_user_type_group(cr, [1, u2id])


def one_user_type_group(cr, admin_ids):
    admin_ids = tuple(admin_ids)
    user = util.ref(cr, "base.group_user")
    portal = util.ref(cr, "base.group_portal")
    public = util.ref(cr, "base.group_public")
    settings = util.ref(cr, "base.group_system")
    accessrights = util.ref(cr, "base.group_erp_manager")
    usability = util.ref(cr, "base.module_category_usability")
    # remove public users from all other non usability groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid != %(public)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id = %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(public)s)
                AND uid NOT IN %(admin_ids)s
    """, locals())

    # remove portal users from all other non usability group
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid != %(portal)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id = %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(portal)s)
                AND uid NOT IN %(admin_ids)s
    """, locals())

    # remove SUPERUSER and user2 from `portal` and `public` groups
    cr.execute("""
        DELETE FROM res_groups_users_rel
              WHERE gid IN (%(portal)s, %(public)s)
                AND uid IN %(admin_ids)s
    """, locals())
    # and force them to `employee`, `settings` and `access rights` groups
    util.fixup_m2m(cr, 'res_groups_users_rel', 'res_users', 'res_groups', 'uid', 'gid')
    for admin_id in admin_ids:
        cr.execute("""
            INSERT INTO res_groups_users_rel(uid, gid)
                 VALUES (%(admin_id)s, %(user)s), (%(admin_id)s, %(settings)s), (%(admin_id)s, %(accessrights)s)
            ON CONFLICT DO NOTHING
        """, locals())
