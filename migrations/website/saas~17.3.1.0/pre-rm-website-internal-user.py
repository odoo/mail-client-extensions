from odoo.upgrade import util


def migrate(cr, version):
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
