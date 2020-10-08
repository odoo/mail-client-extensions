# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_graphene.graphene_google_map")

    util.remove_record(cr, "theme_graphene._assets_utils")
    util.remove_record(cr, "theme_graphene._assets_frontend_helpers")
    util.remove_record(cr, "theme_graphene.assets_frontend")
    util.remove_record(cr, "theme_graphene.assets_editor")
    util.remove_record(cr, "theme_graphene.option_font_playfair")
    util.remove_record(cr, "theme_graphene.option_font_sourcesans")
    util.remove_record(cr, "theme_graphene.graphene_top_content_options")
    util.remove_record(cr, "theme_graphene.snippet_options")
    util.remove_record(cr, "theme_graphene.graphene_bg_effects")
    util.remove_record(cr, "theme_graphene.graphene_typo_pattern")
    util.remove_record(cr, "theme_graphene.graphene_colorpicker_pattern")
    util.remove_record(cr, "theme_graphene.snippet_selection")
