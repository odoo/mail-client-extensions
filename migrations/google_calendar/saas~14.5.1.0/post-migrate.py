# -*- coding:utf-8 -*-

from odoo import SUPERUSER_ID

from odoo.upgrade import util


def migrate(cr, version):
    """
    google_calendar move google credentials (tokens) from res_users to a dedicated table
    """

    cr.execute("UPDATE res_users SET google_calendar_token = NULL WHERE id = %s", [SUPERUSER_ID])

    cr.execute(
        """
        UPDATE res_users u
           SET google_calendar_token = null
          FROM res_partner p
         WHERE u.google_calendar_token is not null
           AND EXISTS(SELECT 1 FROM res_users u2
                              WHERE u2.google_calendar_token = u.google_calendar_token
                                AND u2.id < u.id)
           AND p.id = u.partner_id
     RETURNING p.name;
        """
    )
    users = ", ".join([name for name, in cr.fetchall()])
    if users:
        util.add_to_migration_reports(
            message=f"""
            The Google credentials from the following users were the same as other users:
                {users}.
            Google credentials are unique per user, so they have been removed to allow the upgrade to continue.
            """,
            category="Users",
        )

    # Migrate the google token into a dedicated table
    cr.execute(
        """
        WITH gcc_insert AS (
            INSERT INTO google_calendar_credentials (
                            calendar_rtoken,calendar_token,
                            calendar_token_validity,
                            calendar_sync_token,
                            calendar_cal_id,
                            synchronization_stopped
                        )
                 SELECT google_calendar_rtoken,
                        google_calendar_token,
                        google_calendar_token_validity,
                        google_calendar_sync_token,
                        google_calendar_cal_id,
                        google_synchronization_stopped
                   FROM res_users
                  WHERE google_calendar_token is not null
              RETURNING id,calendar_token
        )
        UPDATE res_users
           SET google_cal_account_id = gcc_insert.id
          FROM gcc_insert
         WHERE gcc_insert.calendar_token=res_users.google_calendar_token
        """
    )
    # Those are related fields now
    util.remove_column(cr, "res_users", "google_calendar_rtoken")
    util.remove_column(cr, "res_users", "google_calendar_token")
    util.remove_column(cr, "res_users", "google_calendar_token_validity")
    util.remove_column(cr, "res_users", "google_calendar_sync_token")
    util.remove_column(cr, "res_users", "google_calendar_cal_id")
    util.remove_column(cr, "res_users", "google_synchronization_stopped")
