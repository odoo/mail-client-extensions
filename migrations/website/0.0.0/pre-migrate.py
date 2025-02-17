from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Index removed on https://github.com/odoo/odoo/pull/37901 (13.0)
    if util.version_between("13.0", "18.0"):
        cr.execute("DROP INDEX IF EXISTS res_users_login_key_unique_website_index")
    if util.version_gte("saas~17.3"):
        cr.execute(
            """
            UPDATE res_users u
               SET website_id = NULL
              FROM res_groups_users_rel rel
             WHERE rel.uid = u.id
               AND rel.gid = %s
               AND u.website_id IS NOT NULL
            """,
            [util.ref(cr, "base.group_user")],
        )
