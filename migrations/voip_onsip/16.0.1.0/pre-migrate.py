from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "res_users_settings", "onsip_auth_username", "varchar")

    cr.execute(
        """
 INSERT INTO res_users_settings(user_id, onsip_auth_username)
      SELECT id, onsip_auth_user
        FROM res_users
       WHERE NULLIF(TRIM(onsip_auth_user), '') IS NOT NULL
 ON CONFLICT (user_id) DO UPDATE
            SET onsip_auth_username = EXCLUDED.onsip_auth_username
    """
    )

    util.remove_column(cr, "res_users", "onsip_auth_user")
    util.rename_field(cr, "res.users", "onsip_auth_user", "onsip_auth_username")
