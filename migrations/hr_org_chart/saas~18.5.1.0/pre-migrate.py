from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_org_chart.res_users_view_form")
