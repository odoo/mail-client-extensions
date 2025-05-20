from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_company_car")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_new_car")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_public")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_train")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_private_car")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_private_bike")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_transport_company_bike")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_internet")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_mobile")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_extra_time_off")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_intellectual_property")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_representation_fees")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_fuel_card")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_yearly_commission")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_meal_vouchers")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_eco_voucher")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_thirteen_month")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_double_holiday")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_hospital_insurance")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_spouse")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_children")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_insured_adults")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_hospital_insurance_note")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_group_insurance")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insurance")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_spouse")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_children")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insured_adults")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_ambulatory_insurance_note")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.l10n_be_mobility_budget_amount")

    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.hr_contract_salary_payroll_resume_gross_cp200")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.hr_contract_salary_resume_final_yearly_costs")
    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.hr_contract_salary_resume_extra_time_off")

    util.update_record_from_xml(cr, "l10n_be_hr_contract_salary.hr_payroll_dashboard_warning_ip_eligible_contract")
    util.update_record_from_xml(
        cr, "l10n_be_hr_contract_salary.hr_payroll_dashboard_warning_employee_without_exemption"
    )
