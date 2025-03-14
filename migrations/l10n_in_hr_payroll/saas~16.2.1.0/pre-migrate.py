from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in_hr_payroll.report_india_payslip")
    util.remove_view(cr, "l10n_in_hr_payroll.view_res_company_da")

    # Removed salary structures and types
    util.delete_unused(cr, "l10n_in_hr_payroll.structure_0002")
    util.delete_unused(cr, "l10n_in_hr_payroll.structure_worker_0001")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_payroll_salary_structure_ind_emp")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_payroll_salary_structure_type_ind_emp")

    # Removed salary rules
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_da")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_trans_allownce")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_lta")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_le")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_performance")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_bonus")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_salary_rule_medical_allow")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_payslip_line_professional_tax")
    util.delete_unused(cr, "l10n_in_hr_payroll.hr_payslip_rule_employee_esic")

    util.rename_field(cr, "res.company", "dearness_allowance", "l10n_in_dearness_allowance")

    for field in ["uan", "pan", "esic_number"]:
        util.rename_field(cr, "hr.employee", field, f"l10n_in_{field}")

    for field in [
        "tds",
        "driver_salay",
        "medical_insurance",
        "voluntary_provident_fund",
        "house_rent_allowance_metro_nonmetro",
        "supplementary_allowance",
    ]:
        util.rename_field(cr, "hr.contract", field, f"l10n_in_{field}")
