# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_treehouse.treehouse_options")

    util.remove_record(cr, "theme_treehouse.assets_frontend")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_01")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_02")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_03")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_04")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_05")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_06")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_07")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_08")
    util.remove_record(cr, "theme_treehouse.body_bg_pattern_09")
    util.remove_record(cr, "theme_treehouse.preheader")
    util.remove_record(cr, "theme_treehouse.add_footer_arrow")
    util.remove_record(cr, "theme_treehouse.assets_snippet_s_blockquote_css_000")
    util.remove_record(cr, "theme_treehouse._assets_snippet_s_masonry_block_css_000_variables")
    util.remove_record(cr, "theme_treehouse.assets_snippet_s_three_columns_css_000")
    util.remove_record(cr, "theme_treehouse._assets_utils")
    util.remove_record(cr, "theme_treehouse.snippets_selection")
    util.remove_record(cr, "theme_treehouse.s_share_extended")
