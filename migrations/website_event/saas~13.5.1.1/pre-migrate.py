# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # gone views (stolen from `website_event_online`)
    gone_views = """
        event_event_view_form
        event_type_view_form
        event_layout_main
        event_tag_view_form
        event_tag_view_list
        event_tag_category_view_list
        event_tag_category_view_form
    """
    for view in util.splitlines(gone_views):
        util.remove_view(cr, f"website_event.{view}")
    # internal renaming
    util.rename_xmlid(cr, *eb("website_event.event_event_view_form{_inherit_website,}"))
    util.rename_xmlid(cr, *eb("website_event.event_event_view_list{_inherit_website,}"))
    util.rename_xmlid(cr, *eb("website_event.event_type_view_form{_inherit_website,}"))

    # website menu model move
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_search"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_form"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_tree"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_action"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.menu_website_event_menu"))

    # models
    util.move_model(cr, "website.event.menu", "website_event_track", "website_event", move_data=True)

    for model in {"event", "type"}:
        util.create_column(cr, f"event_{model}", "menu_register_cta", "boolean", default=False)
        util.create_column(cr, f"event_{model}", "community_menu", "boolean", default=False)
