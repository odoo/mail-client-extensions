# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    microsoft_calendar do not sync old events (PR: 128150 community).
    """
    # Create Microsoft Credentials table.
    cr.execute(
        """
        CREATE TABLE microsoft_calendar_credentials (
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,

            calendar_sync_token varchar,
            synchronization_stopped boolean,
            last_sync_date timestamp without time zone
        )
    """
    )

    # Create reference to Microsoft Credentials inside res_users.
    util.create_column(cr, "res_users", "microsoft_calendar_account_id", "int4")

    # Migrate the Microsoft token from res_users to Microsoft Credentials.
    cr.execute(
        """
        WITH mcc_insert AS (
            INSERT INTO microsoft_calendar_credentials (
                            calendar_sync_token,
                            synchronization_stopped
                        )
                 SELECT microsoft_calendar_sync_token,
                        microsoft_synchronization_stopped
                   FROM res_users
                  WHERE microsoft_calendar_sync_token is not null
              RETURNING id,calendar_sync_token
        )
        UPDATE res_users
           SET microsoft_calendar_account_id = mcc_insert.id
          FROM mcc_insert
         WHERE mcc_insert.calendar_sync_token=res_users.microsoft_calendar_sync_token
        """
    )

    # Remove old fields from res_users, these fields will be related now.
    util.remove_column(cr, "res_users", "microsoft_calendar_sync_token")
    util.remove_column(cr, "res_users", "microsoft_synchronization_stopped")
