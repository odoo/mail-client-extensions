# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_ui_view", "visibility", "varchar")
    util.create_column(cr, "ir_ui_view", "visibility_group", "int4")
    util.create_column(cr, "ir_ui_view", "visibility_password", "varchar")

    if util.table_exists(cr, "theme_ir_ui_view"):
        util.create_column(cr, "theme_ir_ui_view", "customize_show", "boolean")

    util.create_column(cr, "website", "google_search_console", "varchar")

    # from `website_theme_install` module (merged into `website`)
    util.remove_view(cr, "website.website_theme_install_assets")
    util.remove_view(cr, "website.customize_show")
