# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rename_models = [
        "hr.contract.salary.advantage",
        "hr.contract.salary.advantage.value",
        "hr.contract.salary.advantage.type",
    ]

    for model in rename_models:
        util.rename_model(cr, model, model.replace("advantage", "benefit"))

    util.rename_field(cr, "hr.contract.salary.benefit", "advantage_type_id", "benefit_type_id")
    util.rename_field(cr, "hr.contract.salary.benefit", "advantage_ids", "benefit_ids")
    util.rename_field(cr, "hr.contract.salary.benefit.value", "advantage_id", "benefit_id")
    util.rename_field(cr, "hr.contract.salary.resume", "advantage_ids", "benefit_ids")
    util.rename_field(cr, "hr.payroll.structure.type", "salary_advantage_ids", "salary_benefits_ids")

    rename_records = [
        # records
        "hr_contract_salary.hr_contract_salary_resume_category_monthly_advantages",
        "hr_contract_salary.hr_contract_salary_resume_category_yearly_advantages",
        "hr_contract_salary.l10n_be_non_financial_advantages",
        "hr_contract_salary.advantage_extra_time_off",
        # menu/action
        "hr_contract_salary.hr_contract_advantage_action",
        "hr_contract_salary.salary_package_advantage",
        # views/templates
        "hr_contract_salary.salary_package_advantages",
        "hr_contract_salary.hr_contract_advantage_view_form",
        "hr_contract_salary.hr_contract_advantage_view_search",
        "hr_contract_salary.hr_contract_advantage_view_tree",
    ]
    for record in rename_records:
        util.rename_xmlid(cr, record, record.replace("advantage", "benefit"))
