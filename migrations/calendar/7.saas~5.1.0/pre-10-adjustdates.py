# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.release import series
from openerp.tools.parse_version import parse_version as pv

def migrate(cr, version):
    util.rename_field(cr, 'calendar.event', 'end_date', 'final_date')

    util.rename_field(cr, 'calendar.event', 'date', 'start_datetime')
    util.rename_field(cr, 'calendar.event', 'date_deadline', 'stop_datetime')
    util.create_column(cr, 'calendar_event', 'start_date', 'date')
    util.create_column(cr, 'calendar_event', 'stop_date', 'date')
    util.create_column(cr, 'calendar_event', 'display_start', 'varchar')
    util.create_column(cr, 'calendar_event', 'start', 'timestamp without time zone')
    util.create_column(cr, 'calendar_event', 'stop', 'timestamp without time zone')

    cr.execute("""UPDATE calendar_event
                     SET start_date = start_datetime + interval '12 hours',
                     stop_date = stop_datetime + interval '12 hours'
                   WHERE allday = 't'
               """)
    cr.execute("""UPDATE calendar_event
                     SET stop_date = start_date + (duration * interval '1 hour')
                   WHERE duration IS NOT NULL
                     AND stop_date IS NULL
                     AND allday = 't'
               """)
    cr.execute("""UPDATE calendar_event
                     SET stop_datetime = start_datetime + (duration * interval '1 hour')
                   WHERE duration IS NOT NULL
                     AND stop_datetime IS NULL
                     AND allday = 'f'
               """)
    cr.execute("""UPDATE calendar_event
                     SET display_start = CASE WHEN allday = 't'
                                              THEN to_char(start_date,'YYYY-MM-DD')
                                              ELSE to_char(start_datetime, 'YYYY-MM-DD HH24:MI:SS')
                                          END,
                         start = CASE WHEN allday = 't' THEN start_date ELSE start_datetime END,
                         stop = CASE WHEN allday = 't' THEN stop_date ELSE stop_datetime END
               """)

    # force update event views
    cr.execute("""UPDATE ir_model_data d
                     SET noupdate=%s
                    FROM ir_ui_view v
                   WHERE d.model=%s
                     AND d.res_id=v.id
                     AND v.model=%s
               """, (False, 'ir.ui.view', 'calendar.event'))

    # update email templates
    table = "mail_template" if pv(series) >= pv("8.saas~6") else "email_template"
    cr.execute("""UPDATE {table}
                     SET body_html=REPLACE(REPLACE(body_html, %s, %s), %s, %s)
                   WHERE model_id=(SELECT id FROM ir_model WHERE model=%s)
               """.format(table=table),
               ("object.event_id.display_time",
                "object.event_id.get_display_time_tz(tz=object.partner_id.tz)",
                "object.event_id.date",
                "object.event_id.start",
                "calendar.attendee"))
