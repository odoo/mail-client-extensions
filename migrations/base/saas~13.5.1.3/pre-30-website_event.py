# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # fields move from _online, directly to event
    util.move_field_to_module(cr, "event.tag", "color", "website_event_online", "event")

    # fields move from _online: remaining in website_event
    util.move_field_to_module(cr, "event.event", "menu_register_cta", "website_event_online", "website_event")
    util.move_field_to_module(cr, "event.event", "is_ongoing", "website_event_online", "website_event")
    util.move_field_to_module(cr, "event.event", "is_done", "website_event_online", "website_event")
    util.move_field_to_module(cr, "event.event", "start_today", "website_event_online", "website_event")
    util.move_field_to_module(cr, "event.event", "start_remaining", "website_event_online", "website_event")

    util.move_field_to_module(cr, "event.registration", "visitor_id", "website_event_online", "website_event")

    util.move_field_to_module(cr, "website.visitor", "parent_id", "website_event_online", "website_event")
    util.move_field_to_module(cr, "website.visitor", "event_registration_ids", "website_event_online", "website_event")
    util.move_field_to_module(
        cr, "website.visitor", "event_registration_count", "website_event_online", "website_event"
    )
    util.move_field_to_module(cr, "website.visitor", "event_registered_ids", "website_event_online", "website_event")

    # fields move from track_online to remove
    util.move_field_to_module(cr, "event.event", "community_menu", "website_event_track_online", "website_event")
    util.move_field_to_module(cr, "event.event", "community_menu_ids", "website_event_track_online", "website_event")

    util.move_field_to_module(cr, "event.type", "community_menu", "website_event_track_online", "website_event")

    # move some demo data to avoid issues
    for xml_id in [
        "website_visitor_event_0",
        "website_visitor_event_1",
        "website_visitor_event_2",
        "website_visitor_event_2_1",
    ]:
        util.rename_xmlid(cr, *eb("{website_event_online,website_event}.%s" % xml_id))

    # finally remove module now that we moved fields and records to keep
    util.remove_module(cr, "website_event_online")
