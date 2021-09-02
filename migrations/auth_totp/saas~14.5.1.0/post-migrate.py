# -*- coding: utf-8 -*-


def migrate(cr, version):

    cr.execute(
        """
        INSERT INTO auth_totp_device (name, user_id, scope, create_date, index, key)
        SELECT a.name, a.user_id, 'browser', a.create_date, a.index, a.key
        FROM res_users_apikeys a
        WHERE a.scope = '2fa_trusted_device'
        """
    )
    cr.execute("DELETE FROM res_users_apikeys WHERE scope = '2fa_trusted_device'")
