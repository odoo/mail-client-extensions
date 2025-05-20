from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(
        cr, "l10n_ae_hr_payroll.l10n_ae_hr_payroll_uae_employee_payroll_structure_basic_salary_rule"
    )
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_housing_allowance_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_transportation_allowance_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_other_allowances_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_end_of_service_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_end_of_service_provision_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_annual_leave_provision_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_social_insurance_company_contribution_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_social_insurance_employee_contribution_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_sick_leave_50_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_sick_leave_0_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_dews_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_unpaid_leave_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_out_of_contract_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_annual_leaves_eos_allowance_salary_rule")
    util.update_record_from_xml(cr, "l10n_ae_hr_payroll.uae_annual_leaves_eos_deduction_salary_rule")
