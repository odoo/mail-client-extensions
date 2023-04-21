# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "is_multipage", "boolean", default=False)  # Skip _compute
