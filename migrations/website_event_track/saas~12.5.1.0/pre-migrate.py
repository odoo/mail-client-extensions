# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM event_track_tag WHERE name IS NULL")

    util.create_column(cr, "event_track", "date_end", "timestamp without time zone")
    cr.execute("UPDATE event_track SET date_end = date + ('1 hour'::interval * duration)")

    util.rename_field(cr, "event.sponsor", "image_medium", "image_128")

    for template in {"track", "track_view", "event_sponsor", "event_track_proposal"}:
        util.force_noupdate(cr, "website_event_track." + template, noupdate=False)
