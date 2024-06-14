from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_salary_arrears_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_other_earnings_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_salary_deduction_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_other_deduction_salary_rule")
