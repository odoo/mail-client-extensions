# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'invitation changedate reminder'.split():
        util.force_noupdate(cr, 'calendar.calendar_template_meeting_' + t, False)

    util.rename_field(cr, 'calendar.attendee', 'cn', 'common_name')
