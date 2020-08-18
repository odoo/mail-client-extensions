# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # internal renaming
    util.rename_xmlid(cr, "website_event.event_event_view_form_inherit_website", "website_event.event_event_view_form")
    util.rename_xmlid(cr, "website_event.event_event_view_list_inherit_website", "website_event.event_event_view_list")
    util.rename_xmlid(cr, "website_event.event_type_view_form_inherit_website", "website_event.event_type_view_form")

    # website menu model move
    util.move_model(cr, "website.event.menu", "website_event_track", "website_event", move_data=True)
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_search"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_form"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_view_tree"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.website_event_menu_action"))
    util.rename_xmlid(cr, *eb("{website_event_track,website_event}.menu_website_event_menu"))
