# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_real_estate._assets_frontend_helpers")
    util.remove_record(cr, "theme_real_estate.assets_frontend")
