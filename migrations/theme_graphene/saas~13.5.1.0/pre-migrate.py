# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_graphene.graphene_google_map")

    util.remove_record(cr, "theme_graphene._assets_utils")
    util.remove_record(cr, "theme_graphene._assets_frontend_helpers")
    util.remove_record(cr, "theme_graphene.assets_frontend")
    util.remove_record(cr, "theme_graphene.assets_editor")
