# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "web_editor.wysiwyg_iframe_css_assets")
    util.remove_view(cr, "web_editor.wysiwyg_snippets")
