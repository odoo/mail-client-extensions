from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll_partena.hr_employee_form_l10n_be_hr_payroll_partena")
