from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "auth_totp_wizard", "code")
