# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_avantgarde.avantgarde_google_map")

    util.remove_record(cr, "theme_avantgarde._assets_utils")
    util.remove_record(cr, "theme_avantgarde._assets_frontend_helpers")
    util.remove_record(cr, "theme_avantgarde.assets_frontend")
    util.remove_record(cr, "theme_avantgarde.assets_editor")
    util.remove_record(cr, "theme_avantgarde.avantgarde_option_layout_pre_header")
    util.remove_record(cr, "theme_avantgarde.avantgarde_option_layout_hide_year")
    util.remove_record(cr, "theme_avantgarde.avantgarde_header")
    util.remove_record(cr, "theme_avantgarde.avantgarde_top_content_options")
    util.remove_record(cr, "theme_avantgarde.snippet_options")
    util.remove_record(cr, "theme_avantgarde.avantgarde_option_layout_pre_header")
    util.remove_record(cr, "theme_avantgarde.avantgarde_option_layout_hide_year")
    util.remove_record(cr, "theme_avantgarde.avant_data-selectors")
    util.remove_record(cr, "theme_avantgarde.avantgarde_colorpicker_pattern")
    util.remove_record(cr, "theme_avantgarde.avantgarde_bg_effects")
    util.remove_record(cr, "theme_avantgarde.avantgarde_typo_pattern")
    util.remove_record(cr, "theme_avantgarde.snippet_selection")
