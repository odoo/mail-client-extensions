# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    models = ["calendar.event", "calendar.recurrence"]
    rename_fields = {
        "mo": "mon",
        "tu": "tue",
        "we": "wed",
        "th": "thu",
        "fr": "fri",
        "sa": "sat",
        "su": "sun",
    }
    for model in models:
        for old_name, new_name in rename_fields.items():
            util.rename_field(cr, model, old_name, new_name)

    # Update values of weekday selection field
    cr.execute(
        """
           UPDATE calendar_recurrence
              SET weekday = CASE weekday
                            WHEN 'MO' THEN 'MON'
                            WHEN 'TU' THEN 'TUE'
                            WHEN 'WE' THEN 'WED'
                            WHEN 'TH' THEN 'THU'
                            WHEN 'FR' THEN 'FRI'
                            WHEN 'SA' THEN 'SAT'
                            WHEN 'SU' THEN 'SUN'
                            ELSE weekday
                             END
            WHERE weekday IS NOT NULL
        """
    )

    reminder_template = util.ref(cr, "calendar.calendar_template_meeting_reminder")
    util.create_column(cr, "calendar_alarm", "mail_template_id", "int4")
    util.create_column(cr, "calendar_alarm", "body", "text")

    # pre-fill mail-based reminders with reminder template
    if reminder_template:
        cr.execute(
            """
               UPDATE calendar_alarm
                  SET mail_template_id = %s
                WHERE alarm_type='email'
            """,
            [reminder_template],
        )
