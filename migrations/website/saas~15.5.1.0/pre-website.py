# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Google Analytics Dashboard deprecated
    util.remove_field(cr, "website", "google_management_client_id")
    util.remove_field(cr, "website", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "google_management_client_id")
    util.remove_field(cr, "res.config.settings", "google_management_client_secret")
    util.remove_field(cr, "res.config.settings", "has_google_analytics_dashboard")
