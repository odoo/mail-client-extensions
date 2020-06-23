# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_website_version")
    util.remove_field(cr, "res.config.settings", "module_website_links")

    util.create_column(cr, "website", "cookies_bar", "boolean")
    util.create_column(cr, "website", "robots_txt", "text")

    gone = """
        s_btn
        theme_customize

        website_visitor_view_graph
    """
    for view in util.splitlines(gone):
        util.remove_view(cr, f"website.{view}")

    util.remove_record(cr, "website.theme_install_todo_action")
