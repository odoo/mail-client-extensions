# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event_track.event_layout")
    util.remove_view(cr, "website_event_track.website_visitor_view_kanban")

    # remove sponsor views as sponsor model is now located in website_event_exhibitor
    # and those views are complete (old _track + _track_exhibitor) -> old ones
    # have no use anymore, let us keep fresh one only
    util.remove_view(cr, "website_event_track.event_sponsor_view_tree")
    util.remove_view(cr, "website_event_track.event_sponsor_view_form")
    util.remove_view(cr, "website_event_track.event_sponsor_view_search")
    util.remove_view(cr, "website_event_track.event_sponsor_view_kanban")

    util.remove_record(cr, "website_event_track.event_sponsor_action_from_event")

    if not util.module_installed(cr, "website_event_exhibitor"):
        util.remove_model(cr, "event.sponsor")
        util.remove_model(cr, "event.sponsor.type")
        util.remove_field(cr, "event.event", "sponsor_ids")
        util.remove_field(cr, "event.event", "sponsor_count")

        util.remove_view(cr, "website_event_track.event_sponsor")
        util.remove_view(cr, "website_event_track.event_sponsor_type_view_tree")
        util.remove_view(cr, "website_event_track.event_sponsor_type_view_form")
        util.remove_record(cr, "website_event_track.event_sponsor_type_action")
        util.remove_menus(cr, [util.ref(cr, "website_event_track.menu_event_sponsor_type")])
