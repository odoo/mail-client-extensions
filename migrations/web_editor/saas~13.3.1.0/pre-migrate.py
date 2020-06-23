# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_attachment", "original_id", "integer")

    util.rename_xmlid(cr, "web_editor.summernote", "web_editor.assets_summernote")
