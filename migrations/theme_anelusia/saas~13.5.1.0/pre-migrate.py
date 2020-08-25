# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_anelusia._assets_secondary_variables")
    util.remove_record(cr, "theme_anelusia.assets_frontend")
    util.remove_record(cr, "theme_anelusia.snippet_options")
    util.remove_record(cr, "theme_anelusia.option_layout_hamburger")
    util.remove_record(cr, "theme_anelusia.assets_snippet_s_numbers_css_000")
