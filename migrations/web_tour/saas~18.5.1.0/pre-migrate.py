from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "web_tour.res_users_view_form")
