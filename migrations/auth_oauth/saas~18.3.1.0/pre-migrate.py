from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "auth_oauth.login")
    util.remove_view(cr, "auth_oauth.signup")
    util.remove_view(cr, "auth_oauth.reset_password")
