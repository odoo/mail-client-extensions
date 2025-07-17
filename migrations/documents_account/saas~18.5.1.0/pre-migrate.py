from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "documents_account_settings")
    util.remove_field(cr, "res.company", "documents_account_settings")
