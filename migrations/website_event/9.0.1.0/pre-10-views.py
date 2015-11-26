# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        index
        event_category
        layout
        template_location
        event_details

        # for csrf
        registration_template
        registration_attendee_details
    """)
    for v in views:
        util.force_noupdate(cr, 'website_event.' + v, False)
