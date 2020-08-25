# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_loftspace.assets_frontend")
    util.remove_record(cr, "theme_loftspace.assets_snippet_s_color_blocks_2_css_000")
    util.remove_record(cr, "theme_loftspace.assets_snippet_s_numbers_css_000")
    util.remove_record(cr, "theme_loftspace._assets_snippet_s_product_list_css_000_variables")
