# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_monglia._assets_frontend_helpers")
    util.remove_record(cr, "theme_monglia.assets_frontend")
    util.remove_record(cr, "theme_monglia.snippet_options")
    util.remove_record(cr, "theme_monglia.website_custom_navigation")
    util.remove_record(cr, "theme_monglia.website_custom_navigation_variables")
    util.remove_record(cr, "theme_monglia.option_navigation_right_style")
    util.remove_record(cr, "theme_monglia.snippet_selection")
