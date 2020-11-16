# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # move sponsor model and fields from _track to _exhibitor
    util.move_model(cr, "event.sponsor", "website_event_track", "website_event_exhibitor", move_data=True)
    util.move_model(cr, "event.sponsor.type", "website_event_track", "website_event_exhibitor", move_data=True)
    util.move_field_to_module(cr, "event.event", "sponsor_ids", "website_event_track", "website_event_exhibitor")
    util.move_field_to_module(cr, "event.event", "sponsor_count", "website_event_track", "website_event_exhibitor")
