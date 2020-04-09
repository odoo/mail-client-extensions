# -*- coding: utf-8 -*-

from datetime import datetime
from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
		INSERT INTO calendar_recurrence (
			base_event_id,
			event_tz,
			rrule_type,
			rrule,
			end_type,
			interval,
			count,
			mo, tu, we, th, fr, sa, su,
			month_by,
			day,
			weekday,
			byday,
			until
		)
			SELECT
				id AS base_event_id,
				event_tz,
				rrule_type,
				rrule,
				end_type,
				interval,
				count,
				mo, tu, we, th, fr, sa, su,
				month_by,
				day,
				week_list AS weekday,
				byday,
				final_date AS until
			FROM calendar_event
			WHERE recurrency=TRUE
		"""
    )
    cr.execute(
        """
		UPDATE calendar_event e SET recurrence_id = r.id
		FROM calendar_recurrence r
		WHERE e.id = r.base_event_id;
		"""
    )
    # Recurrence fields
    for col in "event_tz rrule_type rrule interval count mo tu we th fr sa su day byday".split():
        util.remove_column(cr, "calendar_event", col)

    util.remove_field(cr, "calendar.event", "week_list")
    util.remove_field(cr, "calendar.event", "final_date")

    # Other fields
    for field in "start_datetime stop_datetime display_start state is_attendee recurrent_id recurrent_id_date".split():
        util.remove_field(cr, "calendar.event", field)

    util.remove_column(cr, "calendar_attendee", "email")  # now a related field

    # overwrite mail templates :/
    util.update_record_from_xml(cr, "calendar.calendar_template_meeting_invitation")
    util.update_record_from_xml(cr, "calendar.calendar_template_meeting_changedate")

    env = util.env(cr)
    recurrences = env["calendar.recurrence"].search([])
    event_vals = []
    for recurrence in recurrences:
        event = recurrence.base_event_id
        duration = event.stop - event.start
        ranges = recurrence._get_ranges(event.start, duration)
        ranges = ((start, stop) for start, stop in ranges if start != event.start and stop != event.stop)
        event_vals += [
            (
                event.name,
                start,
                stop,
                event.allday,
                event.start_date or None,
                event.stop_date or None,
                event.duration,
                event.description,
                event.privacy or None,
                event.location,
                event.show_as or None,
                event.res_id,
                event.res_model_id.id or None,
                event.res_model,
                event.user_id.id or None,
                event.active,
                event.recurrency,
                recurrence.id,
            )
            for start, stop in ranges
        ]

    cr.executemany(
        """
        INSERT INTO calendar_event (
            name,
            start,
            stop,
            allday,
            start_date,
            stop_date,
            duration,
            description,
            privacy,
            location,
            show_as,
            res_id,
            res_model_id,
            res_model,
            user_id,
            active,
            recurrency,
            recurrence_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
        event_vals
    )

    # Copy all X2many fields from the original event to the newly created events
    # for the recurrence.

    # tags
    cr.execute(
        """
        INSERT INTO meeting_category_rel(event_id, type_id)
             SELECT e.id AS event_id, c.type_id
               FROM meeting_category_rel c
               JOIN calendar_recurrence r ON c.event_id = r.base_event_id
               JOIN calendar_event e ON r.id = e.recurrence_id AND e.id != r.base_event_id
        """
    )

    # partner_ids
    cr.execute(
        """
        INSERT INTO calendar_event_res_partner_rel(calendar_event_id, res_partner_id)
             SELECT e.id AS calendar_event_id, p.res_partner_id
               FROM calendar_event_res_partner_rel p
               JOIN calendar_recurrence r ON p.calendar_event_id = r.base_event_id
               JOIN calendar_event e ON r.id = e.recurrence_id AND e.id != r.base_event_id
        """
    )

    # attendee_ids
    cr.execute(
        """
        INSERT INTO calendar_attendee(event_id, partner_id, state, common_name, availability)
             SELECT e.id AS calendar_event_id, p.res_partner_id, a.state, a.common_name, a.availability
               FROM calendar_event_res_partner_rel p
               JOIN calendar_event e ON p.calendar_event_id = e.id
               JOIN calendar_recurrence r ON r.id = e.recurrence_id AND e.id != r.base_event_id
               JOIN calendar_attendee a ON (a.event_id = r.base_event_id AND a.partner_id = p.res_partner_id)
        """
    )

    # alarm_ids
    cr.execute(
        """
        INSERT INTO calendar_alarm_calendar_event_rel(calendar_event_id, calendar_alarm_id)
             SELECT e.id AS calendar_event_id, a.calendar_alarm_id
               FROM calendar_alarm_calendar_event_rel a
               JOIN calendar_recurrence r ON a.calendar_event_id = r.base_event_id
               JOIN calendar_event e ON r.id = e.recurrence_id AND e.id != r.base_event_id
        """
    )

    # message_follower_ids
    cr.execute(
        """
        INSERT INTO mail_followers(res_model, res_id, partner_id)
             SELECT 'calendar.event' AS res_model, e.id AS res_id, f.partner_id
               FROM mail_followers f
               JOIN calendar_recurrence r ON f.res_id = r.base_event_id AND f.res_model = 'calendar.event'
               JOIN calendar_event e ON r.id = e.recurrence_id AND e.id != r.base_event_id
        """
    )
