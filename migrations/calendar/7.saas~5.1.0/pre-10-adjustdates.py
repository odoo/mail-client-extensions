# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'calendar.event', 'end_date', 'final_date')

    util.rename_field(cr, 'calendar.event', 'date', 'start_datetime')
    util.rename_field(cr, 'calendar.event', 'date_deadline', 'stop_datetime')
    util.create_column(cr, 'calendar_event', 'start_date', 'date')
    util.create_column(cr, 'calendar_event', 'stop_date', 'date')

    cr.execute("""UPDATE calendar_event
                     SET start_date = start_datetime + interval '12 hours',
                     SET stop_date = stop_datetime + interval '12 hours'
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
