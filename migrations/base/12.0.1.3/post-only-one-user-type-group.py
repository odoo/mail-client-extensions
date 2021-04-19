# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    one_user_type_group(cr, {1} | admin_ids(cr))


def admin_ids(cr):
    # patched version from upgrade utils to return ALL the ids
    cr.execute(
        """
        SELECT DISTINCT r.uid
          FROM res_groups_users_rel r
          JOIN res_users u ON r.uid = u.id
         WHERE u.active
           AND r.gid = (SELECT res_id
                          FROM ir_model_data
                         WHERE module = 'base'
                           AND name = 'group_system')
        """
    )
    return {u[0] for u in cr.fetchall()}

def one_user_type_group(cr, admin_ids):
    admin_ids = tuple(admin_ids)
    user = util.ref(cr, "base.group_user")
    portal = util.ref(cr, "base.group_portal")
    public = util.ref(cr, "base.group_public")
    settings = util.ref(cr, "base.group_system")
    accessrights = util.ref(cr, "base.group_erp_manager")
    account_user = util.ref(cr, "account.group_account_user")
    usability = (util.ref(cr, "base.module_category_usability"), util.ref(cr, "base.module_category_hidden"))
    # remove public users from all other non usability groups
    cr.execute(
        """
        DELETE FROM res_groups_users_rel
              WHERE gid != %(public)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id IN %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(public)s)
                AND uid NOT IN %(admin_ids)s
    """,
        locals(),
    )

    # remove portal users from all other non usability group
    cr.execute(
        """
        DELETE FROM res_groups_users_rel
              WHERE gid != %(portal)s
                AND gid NOT IN (SELECT id FROM res_groups WHERE category_id IN  %(usability)s)
                AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid = %(portal)s)
                AND uid NOT IN %(admin_ids)s
    """,
        locals(),
    )

    if account_user:
        # remove group_account_user from all public/portal users
        cr.execute(
            """
            DELETE FROM res_groups_users_rel
                  WHERE gid = %(account_user)s
                    AND uid IN (SELECT uid FROM res_groups_users_rel WHERE gid IN (%(portal)s, %(public)s))
                    AND uid NOT IN %(admin_ids)s
        """,
            locals(),
        )

    # remove SUPERUSER and user2 from `portal` and `public` groups, or groups that implicitly inherit those
    cr.execute(
        """
        WITH RECURSIVE groups AS (
            SELECT gid, hid
              FROM (
                  VALUES (%(portal)s, NULL::int4), (%(public)s, NULL::int4)
                ) g(gid, hid)
            UNION
            SELECT r.gid, r.hid
              FROM res_groups_implied_rel r
              JOIN groups g ON g.gid = r.hid
        )
        DELETE FROM res_groups_users_rel
              WHERE gid IN (
                  SELECT gid FROM groups
                )
                AND uid IN %(admin_ids)s
    """,
        locals(),
    )

    # and force them to `employee`, `settings` and `access rights` groups
    util.fixup_m2m(cr, "res_groups_users_rel", "res_users", "res_groups", "uid", "gid")
    for admin_id in admin_ids:  # noqa
        cr.execute(
            """
            INSERT INTO res_groups_users_rel(uid, gid)
                 VALUES (%(admin_id)s, %(user)s), (%(admin_id)s, %(settings)s), (%(admin_id)s, %(accessrights)s)
            ON CONFLICT DO NOTHING
        """,
            locals(),
        )
