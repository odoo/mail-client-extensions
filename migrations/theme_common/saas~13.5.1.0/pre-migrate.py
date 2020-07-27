# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "theme_common.snippets")
    util.remove_record(cr, "theme_common.s_google_map")
    util.remove_record(cr, "theme_common.s_google_map_option")
