from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_contract_salary.hr_contract_view_form")

    mod = util.import_script("hr_contract_salary/saas~18.4.2.0/pre-hr_version.py")

    xmlids = """
        hr_contract_salary_personal_info_km_home_work
        hr_contract_salary_personal_info_disabled
        hr_contract_salary_personal_info_marital
        hr_contract_salary_personal_info_disabled_spouse_bool
        hr_contract_salary_personal_info_spouse_fiscal_status
        hr_contract_salary_personal_info_spouse_complete_name
        hr_contract_salary_personal_info_spouse_birthdate
        hr_contract_salary_personal_info_children
        hr_contract_salary_personal_info_disabled_children_bool
        hr_contract_salary_personal_info_disabled_children_number
        hr_contract_salary_personal_info_other_dependent_people
        hr_contract_salary_personal_info_other_senior_dependent
        hr_contract_salary_personal_info_other_disabled_senior_dependent
        hr_contract_salary_personal_info_other_juniors_dependent
        hr_contract_salary_personal_info_other_disabled_juniors_dependant
    """
    mod.set_personal_info_to_version(cr, "l10n_be_hr_contract_salary", list(util.splitlines(xmlids)))
