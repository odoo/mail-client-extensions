from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "spreadsheet.template", "data", "spreadsheet_binary_data")
    util.rename_field(cr, "save.spreadsheet.template", "data", "spreadsheet_binary_data")
