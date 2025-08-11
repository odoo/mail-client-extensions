from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "auth_oauth.view_users_form")
