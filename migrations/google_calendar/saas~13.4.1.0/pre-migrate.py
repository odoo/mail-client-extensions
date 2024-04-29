from odoo.upgrade import util


def migrate(cr, version):
    util.remove_constraint(cr, "calendar_attendee", "calendar_attendee_google_id_uniq")

    util.create_column(cr, "calendar_event", "google_id", "varchar")
    util.create_column(cr, "calendar_event", "need_sync", "boolean", default=False)
    util.create_column(cr, "calendar_recurrence", "google_id", "varchar")
    util.create_column(cr, "calendar_recurrence", "need_sync", "boolean", default=False)
    util.create_column(cr, "res_users", "google_calendar_sync_token", "varchar")

    # Google id is currently stored in calendar_attendee
    # Ids are usually the same for all attendees of an event.
    # Google id is from now on stored in calendar_event
    # In case google ids are different between attendees, here is
    # the migration strategy:
    # 1) take the google id from the event owner
    # 2) if it's null, take any other non null google id
    # While this leads to a loss of data it's pretty limited.
    # On our production data we have 252 events linked to more than
    # one google id over a total of ~120k synchronized events.
    cr.execute(
        """
        -- Google id linked to the event owner
        WITH event_owner_google_id AS (
            SELECT a.event_id,
                   a.google_internal_event_id AS google_id,
                   a.oe_synchro_date AS sync_date
              FROM calendar_attendee a
              JOIN res_users u ON u.partner_id = a.partner_id
              JOIN calendar_event e ON e.id = a.event_id
             WHERE e.user_id = u.id
        ),
        -- Any non null google id
        event_google_id AS (
            SELECT a.event_id,
                   MAX(a.google_internal_event_id) AS google_id,
                   MAX(a.oe_synchro_date) AS sync_date
              FROM calendar_attendee a
          GROUP BY event_id
        )
        UPDATE calendar_event e SET google_id = g.google_id, need_sync = g.need_sync FROM (
            SELECT u.event_id,
                   COALESCE(r.google_id, u.google_id) AS google_id,
                   -- No need to sync older events
                   u.sync_date < e2.write_date AND e2.start > '2019-01-01' AS need_sync
              FROM event_google_id u
              JOIN calendar_event e2 ON u.event_id = e2.id
              LEFT JOIN event_owner_google_id r ON u.event_id = r.event_id
        ) AS g
        WHERE g.event_id = e.id
    """
    )
    # google_id from base event => recurrence
    cr.execute(
        """
        UPDATE calendar_recurrence r
           SET google_id = e.google_id
          FROM calendar_event e
         WHERE e.id = r.base_event_id
    """
    )

    # recompute recurring event google_id based on the
    # recurrence google_id
    cr.execute(
        """
        UPDATE calendar_event e
           SET google_id = g.google_id FROM (
        SELECT e.id AS event_id,
               r.google_id || '_' ||
               CASE WHEN e.allday = TRUE
                    THEN to_char(e.start_date, 'YYYYMMDD')
                    ELSE to_char(e.start, 'YYYYMMDD"T"HH24MISS"Z"') END
               AS google_id
          FROM calendar_event e
          JOIN calendar_recurrence r ON r.id = e.recurrence_id AND r.google_id IS NOT NULL
        ) AS g
        WHERE e.id = g.event_id;
        """
    )

    util.update_record_from_xml(cr, "google_calendar.ir_cron_sync_all_cals")

    util.remove_field(cr, "calendar.event", "oe_update_date")
    util.remove_field(cr, "calendar.attendee", "google_internal_event_id")
    util.remove_field(cr, "calendar.attendee", "oe_synchro_date")
    util.remove_field(cr, "res.users", "google_calendar_last_sync_date")
    util.remove_field(cr, "res.config.settings", "server_uri")

    util.remove_model(cr, "google.calendar")
