# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in 'invitation changedate reminder'.split():
        util.force_noupdate(cr, 'calendar.calendar_template_meeting_' + t, False)

    util.rename_field(cr, 'calendar.attendee', 'cn', 'common_name')

    # signature of method `get_interval` used in template has change.
    # Adpat them in case they are in noupdate.
    cr.execute(r"""
        UPDATE mail_template
           SET body_html=regexp_replace(regexp_replace(body_html, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')
               , subject=regexp_replace(regexp_replace(subject, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')

         WHERE model_id = (SELECT id FROM ir_model WHERE model='calendar.attendee')
    """)
    cr.execute(r"""
        UPDATE ir_translation
           SET value = regexp_replace(regexp_replace(value, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')
               , src = regexp_replace(regexp_replace(src, '\ycn\y', 'common_name', 'g'),
                                        '\.get_interval\([^,]+,\s*', '.get_interval(', 'g')

          WHERE name IN ('mail.template,body_html', 'mail.template,subject')
            AND type = 'model'
            AND res_id IN (SELECT id
                             FROM mail_template
                            WHERE model_id = (SELECT id FROM ir_model WHERE model='calendar.attendee')
                           )

    """)
