# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # event.track.tag.category model move
    util.move_model(cr, "event.track.tag.category", "website_event_track_online", "website_event_track", move_data=True)
    for xml_id in [
        "event_track_tag_category_view_form",
        "event_track_tag_category_view_list",
        "event_track_tag_category_action",
        "event_track_tag_category_menu",
    ]:
        util.rename_xmlid(cr, *eb("{website_event_track_online,website_event_track}.%s" % xml_id))

    # event.track.visitor model move
    util.move_model(cr, "event.track.visitor", "website_event_track_online", "website_event_track", move_data=True)
    for xml_id in [
        "event_track_visitor_view_search",
        "event_track_visitor_view_form",
        "event_track_visitor_view_list",
        "event_track_visitor_action",
        "event_track_visitor_menu",
    ]:
        util.rename_xmlid(cr, *eb("{website_event_track_online,website_event_track}.%s" % xml_id))

    # fields move from website_event_track_online
    util.move_field_to_module(cr, "event.sponsor", "name", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.sponsor", "email", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.sponsor", "phone", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.sponsor", "mobile", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.sponsor", "image_512", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.sponsor", "image_256", "website_event_track_online", "website_event_track")
    util.move_field_to_module(
        cr, "event.sponsor", "website_image_url", "website_event_track_online", "website_event_track"
    )

    util.move_field_to_module(cr, "event.track", "is_accepted", "website_event_track_online", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "partner_function", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "partner_company_name", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(cr, "event.track", "website_image", "website_event_track_online", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "website_image_url", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "event_track_visitor_ids", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(cr, "event.track", "is_reminder_on", "website_event_track_online", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "wishlist_visitor_ids", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "wishlist_visitor_count", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "wishlisted_by_default", "website_event_track_online", "website_event_track"
    )

    util.move_field_to_module(
        cr, "event.sponsor.type", "display_ribbon_style", "website_event_track_online", "website_event_track"
    )

    util.move_field_to_module(
        cr, "event.track.stage", "is_accepted", "website_event_track_online", "website_event_track"
    )

    util.move_field_to_module(cr, "event.track.tag", "sequence", "website_event_track_online", "website_event_track")
    util.move_field_to_module(cr, "event.track.tag", "category_id", "website_event_track_online", "website_event_track")

    util.move_field_to_module(
        cr, "website.visitor", "event_track_visitor_ids", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "website.visitor", "event_track_wishlisted_ids", "website_event_track_online", "website_event_track"
    )
    util.move_field_to_module(
        cr, "website.visitor", "event_track_wishlisted_count", "website_event_track_online", "website_event_track"
    )

    # fields move from website_event_track_session
    util.move_field_to_module(cr, "event.track", "website_cta", "website_event_track_session", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "website_cta_title", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "website_cta_url", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "website_cta_delay", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(cr, "event.track", "is_track_live", "website_event_track_session", "website_event_track")
    util.move_field_to_module(cr, "event.track", "is_track_soon", "website_event_track_session", "website_event_track")
    util.move_field_to_module(cr, "event.track", "is_track_today", "website_event_track_session", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "is_track_upcoming", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(cr, "event.track", "is_track_done", "website_event_track_session", "website_event_track")
    util.move_field_to_module(
        cr, "event.track", "track_start_remaining", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "track_start_relative", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "is_website_cta_live", "website_event_track_session", "website_event_track"
    )
    util.move_field_to_module(
        cr, "event.track", "website_cta_start_remaining", "website_event_track_session", "website_event_track"
    )

    # templates move: track_online
    for xml_id in [
        "registration_complete",
        "layout",
        "index",
        "pwa_manifest",
        "agenda_online",
        "agenda_topbar",
        "agenda_topbar_wishlist",
        "agenda_main",
        "agenda_main_track",
        "tracks_wishlist",
        "track_view_wishlist",
    ]:
        util.rename_xmlid(cr, *eb("{website_event_track_online,website_event_track}.%s" % xml_id))
    util.rename_xmlid(cr, "website_event_track_online.offline", "website_event_track.pwa_offline")

    # templates move: track_session
    for xml_id in [
        # main / list view
        "tracks_session",
        "session_topbar",
        "session_topbar_tag",
        "session_topbar_wishlist",
        "tracks_main",
        "tracks_display_cards",
        "tracks_display_list",
        "tracks_cards_track",
        "tracks_search",
        "track_tag_badge_link",
        "track_tag_badge_info",
        # page view
        "event_track_main",
        "event_track_content",
        "event_track_aside",
        "event_track_aside_other_track",
    ]:
        util.rename_xmlid(cr, *eb("{website_event_track_session,website_event_track}.%s" % xml_id))

    # finally remove module now that we moved fields and records to keep
    util.remove_module(cr, "website_event_track_online")
    util.remove_module(cr, "website_event_track_session")
