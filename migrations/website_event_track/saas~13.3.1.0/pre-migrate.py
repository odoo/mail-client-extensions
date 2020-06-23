# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event_track.event_track_social")
    util.remove_record(cr, "website_event_track.access_event_location_manager")

    # Allow archiving of sponsors and get sponsor URL from partner
    util.create_column(cr, "event_sponsor", "active", "boolean", default=True)

    util.fixup_m2m(cr, "event_track_event_track_tag_rel", "event_track", "event_track_tag")
