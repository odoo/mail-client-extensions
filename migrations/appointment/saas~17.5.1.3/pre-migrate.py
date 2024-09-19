from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_field(cr, "appointment.type", "appointment_count_report")

    renames = [
        "appointment.appointment_type_rule_user_{,write_}unlink",
        "appointment.appointment_invite_rule_user{,_internal}",
        "appointment.appointment_invite_rule_user_{,internal_write_}unlink",
        "appointment.appointment_slot_rule_user_{,write_}unlink",
    ]
    for rename in renames:
        util.rename_xmlid(cr, *eb(rename))

    util.remove_menus(cr, [util.ref(cr, "appointment.menu_schedule_report_all")])

    util.create_column(cr, "calendar_event", "appointment_status", "varchar")
    util.explode_execute(
        cr,
        """
        WITH manual_confirmation_events AS (
            SELECT attendee.event_id
              FROM calendar_attendee attendee
              JOIN calendar_event event
                ON event.id = attendee.event_id
              JOIN appointment_type app_type
                ON app_type.id = event.appointment_type_id
               AND app_type.resource_manual_confirmation
             WHERE attendee.state = 'needsAction'
               AND {parallel_filter}
          GROUP BY attendee.event_id
        )
        UPDATE calendar_event event
           SET appointment_status = CASE
                    WHEN event.appointment_type_id IS NULL THEN NULL
                    WHEN event.appointment_attended THEN 'attended'
                    WHEN NOT event.active THEN 'cancelled'
                    WHEN mce IS NOT NULL THEN 'request'
                    ELSE 'booked'
               END
          FROM calendar_event event2
     LEFT JOIN manual_confirmation_events mce
            ON mce.event_id = event2.id
         WHERE event.id = event2.id
           AND {parallel_filter}
        """,
        table="calendar_event",
        alias="event",
    )
    util.remove_field(cr, "calendar.event", "appointment_attended")
    util.rename_field(cr, "appointment.type", *eb("{resource,appointment}_manual_confirmation"))
    util.update_record_from_xml(cr, "calendar.alarm_notif_1")
