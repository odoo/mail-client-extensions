# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "event.tag", "color", "website_event_online", "event")
    util.merge_module(cr, "website_event_online", "website_event")

    util.move_field_to_module(cr, "event.event", "community_menu", "website_event_track_online", "website_event")
    util.move_field_to_module(cr, "event.event", "community_menu_ids", "website_event_track_online", "website_event")
    util.move_field_to_module(cr, "event.type", "community_menu", "website_event_track_online", "website_event")

    util.merge_module(cr, "website_event_track_online", "website_event_track")
    util.merge_module(cr, "website_event_track_session", "website_event_track")
