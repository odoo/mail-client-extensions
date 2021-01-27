# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "has_google_maps")
    util.remove_field(cr, "res.config.settings", "google_maps_api_key")
    util.remove_field(cr, "res.config.settings", "social_twitter")
    util.remove_field(cr, "res.config.settings", "social_facebook")
    util.remove_field(cr, "res.config.settings", "social_github")
    util.remove_field(cr, "res.config.settings", "social_linkedin")
    util.remove_field(cr, "res.config.settings", "social_youtube")
    util.remove_field(cr, "res.config.settings", "social_instagram")
    util.remove_field(cr, "res.config.settings", "has_social_network")
    util.remove_field(cr, "res.config.settings", "specific_user_account")

    if util.module_installed(cr, "website_event"):
        util.move_field_to_module(cr, "website.visitor", "parent_id", "website_event", "website")
        util.remove_record(cr, "website_event.website_visitor_event_0")
        util.remove_record(cr, "website_event.website_visitor_event_1")
        util.remove_record(cr, "website_event.website_visitor_event_2")
        util.remove_record(cr, "website_event.website_visitor_event_2_1")
    else:
        util.create_column(cr, "website_visitor", "parent_id", "int4")
