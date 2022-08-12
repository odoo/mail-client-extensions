# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website.snippet_options_header_brand")

    # Google Analytics Dashboard deprecated
    util.remove_field(cr, "website", "google_management_client_id")
    util.remove_field(cr, "website", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "google_management_client_id")
    util.remove_field(cr, "res.config.settings", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "has_google_analytics_dashboard")
    util.rename_xmlid(
        cr, "website.ir_actions_server_website_google_analytics", "website.ir_actions_server_website_analytics"
    )
    util.rename_xmlid(cr, "website.menu_website_google_analytics", "website.menu_website_analytics")
