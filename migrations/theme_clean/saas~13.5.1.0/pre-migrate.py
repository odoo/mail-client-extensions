# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_clean.assets_frontend")
    util.remove_record(cr, "theme_clean.clean_snippet_options")
    util.remove_record(cr, "theme_clean.snippet_selection")
