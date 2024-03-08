from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "spreadsheet_dashboard", "is_published", "boolean", default=True)
