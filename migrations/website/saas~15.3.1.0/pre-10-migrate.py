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
