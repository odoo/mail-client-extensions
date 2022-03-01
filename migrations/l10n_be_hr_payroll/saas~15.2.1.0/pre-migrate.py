# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_view(cr, "l10n_be_hr_payroll.hr_employee_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payroll_report_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_form_inherit_december")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_group_insurance_wizard_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_december_slip_wizard_view_form")
    util.remove_view(cr, "l10n_be_hr_payroll.dmfa_xml_report_insurance_group")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_individual_account_wizard_view_form")

    # Move data from the merge of `l10n_be_hr_contract_salary_group_insurance` to `l10n_be_hr_contract_salary`.
    # As `l10n_be_hr_contract_salary_group_insurance` depended on `l10n_be_hr_contract_salary`, no need to verify if
    # `l10n_be_hr_contract_salary` is installed. If the xmlid is present, we consider that `l10n_be_hr_contract_salary`
    # is installed.
    advantages = """
        group_insurance
        group_insurance_value_0
        group_insurance_value_2
        group_insurance_value_3

        ambulatory_insurance
        ambulatory_insurance_value_0
        ambulatory_insurance_value_1

        ambulatory_insured_spouse
        ambulatory_insured_children
        ambulatory_insured_adults
    """
    for adv in util.splitlines(advantages):
        util.rename_xmlid(cr, *eb(f"l10n_be_hr_{{payroll,contract_salary}}.l10n_be_{adv}"))

    # and in the other way around from the merge of `l10n_be_hr_payroll_canteen` into `l10n_be_hr_contract_salary`
    util.rename_xmlid(cr, *eb("l10n_be_hr_{contract_salary,payroll}.cp200_employees_salary_canteen"))
    util.move_field_to_module(
        cr, "hr.contract", "l10n_be_canteen_cost", "l10n_be_hr_contract_salary", "l10n_be_hr_payroll"
    )

    util.remove_model(cr, "l10n_be.individual.account.wizard")

    for model in ["281_10", "281_45"]:
        util.remove_field(cr, f"l10n_be.{model}", "pdf_filename")
        util.remove_field(cr, f"l10n_be.{model}", "pdf_file")
        util.move_field_to_module(
            cr, f"l10n_be.{model}", "documents_enabled", "l10n_be_hr_payroll", "documents_l10n_be_hr_payroll"
        )
