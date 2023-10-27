# -*- coding: utf-8 -*-

from psycopg2 import sql

from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/odoo/pull/82863 introduced a hack to save two fields
    # on the same column. It was used to backport changes in stable.
    # Before #82863, microsoft_id was the ms_organizer_event_id (old microsoft_id)
    # which is specific to the Outlook user calendar
    # #82863 introduced the iCalUId which is the same among all Outlook calendars.
    # iCalUId is called ms_universal_event_id
    # After #82863, the microsoft_id column contained oth fields separated by ':'
    # `ms_organizer_event_id` : `ms_universal_event_id``
    # This file update the fields to use one specific column per field

    cr.execute("ALTER TABLE calendar_event RENAME COLUMN microsoft_id TO unified_id")
    cr.execute("ALTER TABLE calendar_recurrence RENAME COLUMN microsoft_id TO unified_id")
    util.create_column(cr, "calendar_event", "microsoft_id", "varchar")
    util.create_column(cr, "calendar_recurrence", "microsoft_id", "varchar")
    util.create_column(cr, "calendar_event", "ms_universal_event_id", "varchar")
    util.create_column(cr, "calendar_recurrence", "ms_universal_event_id", "varchar")
    update_microsoft_ids(cr, "calendar_event")
    update_microsoft_ids(cr, "calendar_recurrence")
    util.remove_field(cr, "calendar.event", "ms_organizer_event_id")
    util.remove_field(cr, "calendar.recurrence", "ms_organizer_event_id")
    util.remove_field(cr, "microsoft.calendar.sync", "ms_organizer_event_id")
    cr.execute("ALTER TABLE calendar_event DROP COLUMN unified_id")
    cr.execute("ALTER TABLE calendar_recurrence DROP COLUMN unified_id")


def update_microsoft_ids(cr, table_name):
    util.explode_execute(
        cr,
        sql.SQL(
            """
            UPDATE {}
            SET microsoft_id=split_part(unified_id, ':', 1),
                ms_universal_event_id=split_part(unified_id, ':', 2)
            WHERE unified_id IS NOT NULL
        """
        )
        .format(sql.Identifier(table_name))
        .as_string(cr._cnx),
        table=table_name,
    )
