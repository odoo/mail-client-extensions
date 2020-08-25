# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "theme_kea.assets_frontend")
    util.remove_record(cr, "theme_kea.kea_snippet_options")
