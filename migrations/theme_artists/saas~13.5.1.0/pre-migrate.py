# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_artists._assets_frontend_helpers")
    util.remove_record(cr, "theme_artists.assets_frontend")
