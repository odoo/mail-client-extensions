# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    for contract_type in ["pfi", "cdi", "cdd"]:
        util.rename_xmlid(
            cr, *eb("{l10n_be_hr_contract_salary,l10n_be_hr_payroll}.l10n_be_contract_type_%s" % (contract_type))
        )

    # Purpose: The related xpath has been merged into l10n_be_hr_payroll.hr_contract_view_form
    util.remove_view(cr, "l10n_be_hr_payroll.hr_contract_view_form_inherit")

    util.remove_model(cr, "l10n_be.meal.voucher.report")

    util.create_column(cr, "hr_contract", "has_hospital_insurance", "boolean")
    util.create_column(cr, "hr_contract", "insured_relative_children", "int4")
    util.create_column(cr, "hr_contract", "insured_relative_adults", "int4")
    util.create_column(cr, "hr_contract", "insured_relative_spouse", "boolean")
    util.create_column(cr, "hr_contract", "hospital_insurance_amount_per_adult", "float8", default=20.5)
    util.create_column(cr, "hr_contract", "hospital_insurance_amount_per_child", "float8", default=7.2)

    util.create_column(cr, "res_config_settings", "hospital_insurance_amount_child", "float8")
    util.create_column(cr, "res_config_settings", "hospital_insurance_amount_adult", "float8")

    util.remove_field(cr, "hr.payslip.employee.depature.notice", "leaving_type")

    # Drop rules with external identifiers
    rules_to_remove = util.splitlines(
        """
        commissions
        gross_salary
        onss_rule
        employment_bonus_employees
        withholding_taxes
        withholding_reduction
        mis_ex_onss
        onss_adjustment
        withholding_taxes_adjustment
        mis_ex_onss_adjustment
        basic_salary_adjustment
        onss_total
        pp_total
        mis_ex_onss_total
        salary_onss_employer
        expense_refund
        attachment_salary
        asignment_salary
        child_support
    """
    )
    for record_to_remove in rules_to_remove:
        util.remove_record(cr, "l10n_be_hr_payroll.cp200_commission_%s" % (record_to_remove))

    # Drop additional rules without xml_ids (Basic, Gross, Net, manually created rules)
    structure_id = util.ref(cr, "l10n_be_hr_payroll.hr_payroll_structure_cp200_structure_commission")

    cr.execute("SELECT id FROM hr_salary_rule WHERE struct_id=%s", [structure_id])
    rule_ids = [row[0] for row in cr.fetchall()]
    for rule_id in rule_ids:
        util.remove_record(cr, ("hr.salary.rule", rule_id))

    # Drop input
    util.remove_record(cr, "l10n_be_hr_payroll.cp200_other_input_commission")

    # Now that no input or rules references the structure, and as the
    # field struct_id is not required on the payslip, the structure can be dropped
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_structure_cp200_structure_commission")

    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.access_hr_payroll_generate_{commission,warrant}_payslips"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.access_hr_payroll_generate_{commission,warrant}_payslips_line"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.hr_payroll_generate_{commission,warrant}_payslips_view_form"))
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.action_hr_payroll_generate_{commission,warrant}_payslips"))

    # As this model comes from the now defunct module `l10n_be_hr_payroll_variable_revenue`,
    # the table may not exists
    util.rename_model(
        cr,
        "hr.payroll.generate.commission.payslips",
        "hr.payroll.generate.warrant.payslips",
        rename_table=util.table_exists(cr, "hr_payroll_generate_commissionw_payslips"),
    )
    util.rename_model(
        cr,
        "hr.payroll.generate.commission.payslips.line",
        "hr.payroll.generate.warrant.payslips.line",
        rename_table=util.table_exists(cr, "hr_payroll_generate_commissionw_payslips_line"),
    )

    util.remove_field(cr, "hr.payroll.generate.warrant.payslips", "commission_type")
