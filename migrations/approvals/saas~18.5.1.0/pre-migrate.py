from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "approvals.res_users_view_form")
