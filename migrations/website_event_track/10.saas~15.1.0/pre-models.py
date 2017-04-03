# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    renames = {
        'count_tracks': 'track_count',
        'count_sponsor': 'sponsor_count',
        'show_tracks': 'website_track',
        'show_track_proposal': 'website_track_proposal',
    }
    for f, t in renames.items():
        util.rename_field(cr, 'event.event', f, t)

    util.create_column(cr, 'event_track', 'kanban_state', 'varchar')
    cr.execute("UPDATE event_track SET kanban_state='normal'")
