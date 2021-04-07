# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # to be removed later when the rename is backported
    if util.column_exists(cr, "ir_asset", "glob"):
        util.rename_field(cr, "ir.asset", "glob", "path")
