from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "hr.contract", "l10n_ae_number_of_days", "l10n_ae_number_of_leave_days")
    util.delete_unused(cr, "l10n_ae_hr_payroll.uae_total_earnings_salary_rule")
