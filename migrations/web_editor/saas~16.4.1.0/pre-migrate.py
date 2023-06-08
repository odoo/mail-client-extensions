# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web_editor.assets_edit_html_field")
    util.remove_view(cr, "web_editor.wysiwyg_iframe_editor_assets")
