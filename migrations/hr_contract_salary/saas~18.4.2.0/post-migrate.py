from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_sex")

    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_sex_male")

    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_sex_female")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_personal_info_sex_other")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_resume_gross")
    util.update_record_from_xml(cr, "hr_contract_salary.hr_contract_salary_resume_final_yearly_costs")

    util.update_record_from_xml(cr, "hr_contract_salary.ir_rule_hr_contract_salary_offer_contract")
    util.update_record_from_xml(cr, "hr_contract_salary.ir_rule_hr_contract_salary_offer_applicant")
