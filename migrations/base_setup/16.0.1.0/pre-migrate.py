from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_google_drive")
    util.remove_field(cr, "res.config.settings", "module_google_spreadsheet")
