from odoo.upgrade import util


def migrate(cr, version):

    # Create new columns on res.users.settings
    util.create_column(cr, "res_users_settings", "external_device_number", "varchar")
    util.create_column(cr, "res_users_settings", "how_to_call_on_mobile", "varchar")
    util.create_column(cr, "res_users_settings", "voip_secret", "varchar")
    util.create_column(cr, "res_users_settings", "voip_username", "varchar")
    util.create_column(cr, "res_users_settings", "should_auto_reject_incoming_calls", "bool")
    util.create_column(cr, "res_users_settings", "should_call_from_another_device", "bool")

    # Create or update res.users.settings with the VoIP config fields from res.users.
    cr.execute(
        """
 INSERT INTO res_users_settings(
                user_id,
                external_device_number,
                should_call_from_another_device,
                should_auto_reject_incoming_calls,
                voip_secret,
                voip_username,
                how_to_call_on_mobile
             )
      SELECT id,
             sip_external_phone,
             sip_always_transfer,
             sip_ignore_incoming,
             sip_password,
             sip_login,
             mobile_call_method
        FROM res_users
       WHERE NULLIF(TRIM(sip_login), '') IS NOT NULL
 ON CONFLICT (user_id) DO UPDATE
            SET external_device_number = EXCLUDED.external_device_number,
                should_call_from_another_device = EXCLUDED.should_call_from_another_device,
                should_auto_reject_incoming_calls = EXCLUDED.should_auto_reject_incoming_calls,
                voip_secret = EXCLUDED.voip_secret,
                voip_username = EXCLUDED.voip_username,
                how_to_call_on_mobile = EXCLUDED.how_to_call_on_mobile;
    """
    )

    # Rename former fields on res.users.
    rename_table = [
        ("mobile_call_method", "how_to_call_on_mobile"),
        ("sip_always_transfer", "should_call_from_another_device"),
        ("sip_external_phone", "external_device_number"),
        ("sip_ignore_incoming", "should_auto_reject_incoming_calls"),
        ("sip_login", "voip_username"),
        ("sip_password", "voip_secret"),
    ]
    for old_name, new_name in rename_table:
        util.remove_column(cr, "res_users", old_name)
        util.rename_field(cr, "res.users", old_name, new_name)
