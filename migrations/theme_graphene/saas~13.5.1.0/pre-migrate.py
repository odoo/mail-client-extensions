# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old snippet options (UI)
    util.remove_record(cr, "theme_graphene.graphene_google_map")
