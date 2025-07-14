from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_us_hr_payroll_account.hr_payslip_run_view_form")
