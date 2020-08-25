# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_bistro.assets_frontend")
    util.remove_record(cr, "theme_bistro.bistro_options")
