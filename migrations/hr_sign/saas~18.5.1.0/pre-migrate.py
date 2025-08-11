from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "sign_request_count")

    util.remove_view(cr, "hr_sign.res_users_request_sign_view_form")
