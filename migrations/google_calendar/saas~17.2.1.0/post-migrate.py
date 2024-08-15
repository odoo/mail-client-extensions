from odoo.upgrade import util


def migrate(cr, version):
    """
    User settings table for calendar users (Community PR:151537).
    """
    # Upsert the Google Calendar Credentials into the Res Users Settings table.
    p, q = (
        (", calendar_default_privacy", ", 'public'")
        if util.column_exists(cr, "res_users_settings", "calendar_default_privacy")
        else ("", "")
    )
    cr.execute(
        f"""
        INSERT INTO res_users_settings (
                        user_id,
                        google_calendar_sync_token,
                        google_calendar_token,
                        google_calendar_rtoken,
                        google_synchronization_stopped,
                        google_calendar_token_validity,
                        google_calendar_cal_id
                        {p}
                    )
             SELECT usr.id,
                    cred_user.calendar_sync_token,
                    cred_user.calendar_token,
                    cred_user.calendar_rtoken,
                    cred_user.synchronization_stopped,
                    cred_user.calendar_token_validity,
                    cred_user.calendar_cal_id
                    {q}
               FROM google_calendar_credentials AS cred_user
               JOIN res_users AS usr
                 ON usr.google_calendar_account_id = cred_user.id
              WHERE cred_user.calendar_rtoken IS NOT NULL
        ON CONFLICT (user_id) DO UPDATE
                SET google_calendar_sync_token = EXCLUDED.google_calendar_sync_token,
                    google_calendar_token = EXCLUDED.google_calendar_token,
                    google_calendar_rtoken = EXCLUDED.google_calendar_rtoken,
                    google_synchronization_stopped = EXCLUDED.google_synchronization_stopped,
                    google_calendar_token_validity = EXCLUDED.google_calendar_token_validity,
                    google_calendar_cal_id = EXCLUDED.google_calendar_cal_id
        """
    )

    # Remove model and its Many2one field in the res_users model.
    util.remove_field(cr, "res.users", "google_calendar_account_id")
    util.remove_model(cr, "google.calendar.credentials")
