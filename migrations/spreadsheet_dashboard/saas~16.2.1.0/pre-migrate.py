from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "spreadsheet.dashboard", "raw", "spreadsheet_data")
