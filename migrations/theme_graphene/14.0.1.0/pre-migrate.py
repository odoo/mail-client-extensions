# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_graphene.option_font_abel")
    util.remove_record(cr, "theme_graphene.option_font_cinzel")
    util.remove_record(cr, "theme_graphene.graphene_option_layout_postcard_variables")
    util.remove_record(cr, "theme_graphene.option_font_sansserif")
    util.remove_record(cr, "theme_graphene.graphene_header")
