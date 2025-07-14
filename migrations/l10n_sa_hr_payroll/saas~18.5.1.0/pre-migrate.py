from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_sa_hr_payroll.hr_payslip_run_view_form")
