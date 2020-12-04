# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_website_version")
    util.remove_field(cr, "res.config.settings", "module_website_links")

    util.create_column(cr, "website", "cookies_bar", "boolean")
    util.create_column(cr, "website", "robots_txt", "text")

    util.remove_view(cr, "website.s_btn")
    util.remove_view(cr, "website.website_visitor_view_graph")
    # The module `test_themes` create a bunch of inherited view without xmlid.
    # We ignore the warnings if the module is installed.
    # Tant pis for the customers that have this test module installed.
    util.remove_view(cr, "website.theme_customize", silent=util.module_installed(cr, "test_themes"))

    util.remove_record(cr, "website.theme_install_todo_action")
