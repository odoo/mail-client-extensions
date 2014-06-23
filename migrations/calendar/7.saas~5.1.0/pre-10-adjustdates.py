# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'calendar.event', 'date', 'start_datetime')
    util.rename_field(cr, 'calendar.event', 'date_deadline', 'stop_datetime')
    util.create_column(cr, 'calendar_event', 'start_date', 'date')
    util.create_column(cr, 'calendar_event', 'stop_date', 'date')
    cr.execute("""UPDATE calendar_event SET start_date = start_datetime WHERE allday = 't'
    """)
    cr.execute("""UPDATE calendar_event SET stop_date = stop_datetime WHERE allday = 't'
    """)
    util.rename_field(cr, 'calendar_event', 'end_date', 'final_date')