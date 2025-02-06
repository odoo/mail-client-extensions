from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "spreadsheet.dashboard", "file_name")
