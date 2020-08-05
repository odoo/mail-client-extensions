# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    env = util.env(cr)
    recurrences = env["calendar.recurrence"].search([])
    not_all_day_ranges = []
    all_day_ranges = []
    recurrences_all_day = recurrences.filtered(lambda r: r._is_allday())
    for recurrence in recurrences - recurrences_all_day:
        event = recurrence.base_event_id
        duration = event.stop - event.start
        ranges = recurrence._get_ranges(event.start, duration)
        not_all_day_ranges += [(recurrence.id, start, stop) for start, stop in ranges]

    for recurrence in recurrences_all_day:
        event = recurrence.base_event_id
        duration = event.stop - event.start
        ranges = recurrence._get_ranges(event.start, duration)
        all_day_ranges += [(recurrence.id, start.date(), stop.date()) for start, stop in ranges]

    cr.executemany(
        """
        UPDATE calendar_event
           SET follow_recurrence = TRUE
         WHERE recurrence_id = %s
           AND start = %s
           AND stop = %s
    """,
        not_all_day_ranges,
    )

    cr.executemany(
        """
        UPDATE calendar_event
           SET follow_recurrence = TRUE
         WHERE recurrence_id = %s
           AND allday = TRUE
           AND start_date = %s
           AND stop_date = %s
    """,
        all_day_ranges,
    )
