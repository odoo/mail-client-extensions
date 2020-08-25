# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_yes._assets_frontend_helpers")
    util.remove_record(cr, "theme_yes.assets_frontend")
