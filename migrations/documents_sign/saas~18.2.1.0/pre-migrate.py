from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "documents_sign_folder_id")
    util.remove_field(cr, "res.company", "documents_sign_folder_id")
