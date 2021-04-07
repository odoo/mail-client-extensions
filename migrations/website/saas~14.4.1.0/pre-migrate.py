# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # TODO: remove later when renaming is backported
    if util.column_exists(cr, "theme_ir_asset", "glob"):
        util.rename_field(cr, "theme.ir.asset", "glob", "path")
