from odoo.upgrade import util


def migrate(cr, version):
    util.merge_model(cr, "spreadsheet.collaborative.mixin", "spreadsheet.mixin")
