from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "spreadsheet.collaborative.mixin", "raw", "spreadsheet_data")
