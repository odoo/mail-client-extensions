from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "auth_totp_mail"):
        util.remove_field(cr, "auth.totp.rate.limit.log", "scope")
        util.move_model(cr, "auth.totp.rate.limit.log", "auth_totp_mail", "auth_totp")
