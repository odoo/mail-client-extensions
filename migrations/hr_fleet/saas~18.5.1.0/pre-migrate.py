from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "employee_cars_count")

    util.remove_view(cr, "hr_fleet.res_users_view_form_preferences")
