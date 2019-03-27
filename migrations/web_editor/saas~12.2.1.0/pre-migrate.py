# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "web_editor.converter.test", "selection")

    util.remove_view(cr, "web_editor.summernote")
    util.remove_view(cr, "web_editor.assets_editor")
    util.remove_view(cr, "web_editor.webclient_bootstrap")
    util.remove_view(cr, "web_editor.js_tests_assets")
    util.remove_view(cr, "web_editor.layout")
    util.remove_view(cr, "web_editor.FieldTextHtml")
