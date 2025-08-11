from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "l10n_lt_working_capacity")

    util.remove_view(cr, "l10n_lt_hr_payroll.res_users_view_form")
