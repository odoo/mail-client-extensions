# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_nano.assets_frontend")
    util.remove_record(cr, "theme_nano.preHeader")
    util.remove_record(cr, "theme_nano.add_footer_arrow")
    util.remove_record(cr, "theme_nano.snippet_options")
    util.remove_record(cr, "theme_nano.option_icons_sidebar")
    util.remove_record(cr, "theme_nano.option_icons_sidebar_right")
    util.remove_record(cr, "theme_nano.option_icons_sidebar_none_variables")
