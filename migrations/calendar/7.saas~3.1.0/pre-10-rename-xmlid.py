# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'calendar.view_crm_meeting_form', 'calendar.view_calendar_event_form')
    util.rename_xmlid(cr, 'calendar.view_crm_meeting_search', 'calendar.view_calendar_event_search')
