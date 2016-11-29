# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'invitation changedate reminder'.split():
        util.force_noupdate(cr, 'calendar.calendar_template_meeting_' + t, False)

    util.rename_field(cr, 'calendar.attendee', 'cn', 'common_name')

    # signature of method `get_interval` used in template has change.
    # Adpat them in case they are in noupdate.
    cr.execute("""
        UPDATE mail_template
           SET body_html=regexp_replace(regexp_replace(body_html, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')
               , subject=regexp_replace(regexp_replace(subject, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')

         WHERE model_id = (SELECT id FROM ir_model WHERE model='calendar.attendee')
    """)
