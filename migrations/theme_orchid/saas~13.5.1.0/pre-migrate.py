# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_orchid.assets_frontend")
    util.remove_record(cr, "theme_orchid._assets_frontend_helpers")
