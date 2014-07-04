# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

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
                  SET display_start = CASE WHEN allday = 't' THEN to_char(start_date,'YYYY-MM-DD') ELSE to_char(start_datetime, 'YYYY-MM-DD HH24:MI:SS') END,
                  start = CASE WHEN allday = 't' THEN start_date ELSE start_datetime END,
                  stop = CASE WHEN allday = 't' THEN stop_date ELSE stop_datetime END""")
