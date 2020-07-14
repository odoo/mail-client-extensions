# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "web_editor.image_optimization_controls", "web_editor.snippet_options_image_optimization_widgets"
    )
