# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

# 4 big changes
# - calendar.alarm + res.alarm are merged into calendar.alarm
# - calendar.event + crm.meeting are merged into calendar.event
# - calendar.event: attendee_ids became a o2m to calendar.attendee
# - calendar.event: alarm_id -> alarm_ids

def migrate(cr, version):
    util.rename_model(cr, 'crm.meeting.type', 'calendar.event.type')

    # temporary column to help migration
    util.create_column(cr, 'crm_meeting', '_mig_event_id', 'int4')

    # create a new crm.meeting for each calendar.event
    # note: month_by still named "select1", will be renamed by the ORM
    cr.execute("""INSERT INTO crm_meeting(create_date, create_uid, write_date, write_uid,
                                          date, date_deadline, duration, "class", location,
                                          show_as, rrule, rrule_type, user_id, active, name,
                                          alarm_id, base_calendar_alarm_id,
                                          recurrency, recurrent_id, recurrent_id_date,
                                          vtimezone, end_type, interval, "count",
                                          mo, tu, we, th, fr, sa, su,
                                          select1, day, week_list, byday, end_date, allday,
                                          state, _mig_event_id
                                         )

                                   SELECT create_date, create_uid, write_date, write_uid,
                                          date, date_deadline, duration, "class", location,
                                          show_as, rrule, rrule_type, user_id, active, name,
                                          alarm_id, base_calendar_alarm_id,
                                          recurrency, recurrent_id, recurrent_id_date,
                                          vtimezone, end_type, interval, "count",
                                          mo, tu, we, th, fr, sa, su,
                                          select1, day, week_list, byday, end_date, allday,

                                          case when state='confirmed' then 'open' else 'draft' end,
                                          id

                                     FROM calendar_event
                      RETURNING id, _mig_event_id
               """)

    for cid, eid in cr.fetchall():
        # copy attendee
        cr.execute("""INSERT INTO meeting_attendee_rel(event_id, attendee_id)
                           SELECT %s, attendee_id
                             FROM event_attendee_rel
                            WHERE event_id=%s""", (cid, eid))

        util.replace_record_references(cr, ('calendar.event', eid), ('crm.meeting', cid))

    cr.execute("ALTER TABLE crm_meeting DROP COLUMN _mig_event_id")

    # in <= saas-2, the link beween attendee and crm.meeting (now calendar.event) was a m2m
    # in >= saas-3, it's a o2m. We need to deduplicate attendees to point to only one event
    # On a side note, calendar.attendee have been cleaned up and now only contain a few
    # fields.
    cr.execute("""SELECT array_agg(event_id), attendee_id
                    FROM meeting_attendee_rel
                GROUP BY attendee_id
                  HAVING count(event_id) >= 2
    """)
    for event_ids, attendee_id in cr.fetchall():
        for event_id in event_ids[1:]:
            # do not copy old cplumns
            cr.execute("""INSERT INTO calendar_attendee(state, cn, partner_id, email, availability)
                               SELECT state, cn, partner_id, email, availability
                                 FROM calendar_attendee
                                WHERE id=%s
                            RETURNING id
                       """, (attendee_id,))
            [new_attendee_id] = cr.fetchone()
            cr.execute("""UPDATE meeting_attendee_rel
                             SET attendee_id=%s
                           WHERE event_id=%s
                             AND attendee_id=%s
                       """, (new_attendee_id, event_id, attendee_id))

    util.create_column(cr, 'calendar_attendee', 'event_id', 'int4')  # FK will be created by the ORM
    cr.execute("""UPDATE calendar_attendee a
                     SET event_id=(SELECT event_id
                                     FROM meeting_attendee_rel
                                    WHERE attendee_id = a.id)""")

    cr.execute("DELETE FROM calendar_attendee WHERE event_id IS NULL")

    # clean attendees
    cr.execute("UPDATE calendar_attendee SET state=%s WHERE state=%s", ('needsAction', 'needs-action'))

    util.delete_model(cr, 'calendar.todo')
    util.delete_model(cr, 'calendar.event')  # reference have already been reassigned
    util.rename_model(cr, 'crm.meeting', 'calendar.event')

    # in <= saas-2, alarms was "instance of alarms"
    # in >= saas-3, alarms are "alarm types" and does not depends of the event or the user/attendee
    # we can simply delete existings alarms
    util.delete_model(cr, 'res.alarm')
    util.delete_model(cr, 'calendar.alarm')
