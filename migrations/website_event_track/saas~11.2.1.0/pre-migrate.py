# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'event_event', 'website_track', 'boolean')
    util.create_column(cr, 'event_event', 'website_track_proposal', 'boolean')

    # real values set in post- script
    cr.execute("UPDATE event_event SET website_track = false, website_track_proposal = false")
