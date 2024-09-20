from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.company", "account_folder", "account_folder_id")
    util.rename_field(cr, "res.config.settings", "account_folder", "account_folder_id")
