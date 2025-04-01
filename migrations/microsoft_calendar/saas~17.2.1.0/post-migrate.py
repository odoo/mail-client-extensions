from odoo.upgrade import util


def migrate(cr, version):
    """
    User settings table for calendar users (Community PR:151537).
    """
    # Upsert the Microsoft Calendar Credentials into the Res Users Settings table.
    if util.column_exists(cr, "res_users_settings", "calendar_default_privacy"):
        privacy = util.format_query(cr, ", {}", "calendar_default_privacy")
        value = util.SQLStr(", 'public'")
        excluded = util.format_query(cr, ", {0} = EXCLUDED.{0}", "calendar_default_privacy")
    else:
        privacy = value = excluded = util.SQLStr("")

    query = util.format_query(
        cr,
        """
        INSERT INTO res_users_settings (
                        user_id,
                        microsoft_calendar_sync_token,
                        microsoft_synchronization_stopped,
                        microsoft_last_sync_date
                        {}
                    )
             SELECT usr.id,
                    cred_user.calendar_sync_token,
                    cred_user.synchronization_stopped,
                    cred_user.last_sync_date
                    {}
               FROM microsoft_calendar_credentials AS cred_user
               JOIN res_users AS usr
                 ON usr.microsoft_calendar_account_id = cred_user.id
              WHERE cred_user.calendar_sync_token IS NOT NULL
        ON CONFLICT (user_id) DO UPDATE SET
                    microsoft_calendar_sync_token = EXCLUDED.microsoft_calendar_sync_token,
                    microsoft_synchronization_stopped = EXCLUDED.microsoft_synchronization_stopped,
                    microsoft_last_sync_date = EXCLUDED.microsoft_last_sync_date
                    {}
        """,
        privacy,
        value,
        excluded,
    )
    cr.execute(query)

    # Remove model and its Many2one field in the res_users model.
    util.remove_field(cr, "res.users", "microsoft_calendar_account_id")
    util.remove_model(cr, "microsoft.calendar.credentials")
