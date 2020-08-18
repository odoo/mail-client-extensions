# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # internal renaming
    util.rename_xmlid(cr, "website_event_track.view_event_form", "website_event_track.event_event_view_form")
    util.rename_xmlid(
        cr,
        "website_event_track.event_event_view_list_inherit_website_event_track",
        "website_event_track.event_event_view_list",
    )

    # deprecated templates to remove
    for xml_id in ["agenda", "tracks", "tracks_filter", "tracks_wishlist", "track_view", "track_view_wishlist"]:
        util.remove_view(cr, "website_event_track.%s" % xml_id)
