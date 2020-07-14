# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Old theme options
    util.remove_record(cr, "theme_bewise.option_layout_hide_menu")

    # Old snippet options (UI)
    util.remove_record(cr, "theme_bewise.options_colorpicker")
