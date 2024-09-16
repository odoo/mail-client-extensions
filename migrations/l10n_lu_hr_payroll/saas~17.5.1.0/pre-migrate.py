from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.hr_payroll_structure_lux_employee_{thirteen,13th}_month"))
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.input_gratification{_lu,}"))

    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_total_deduction")
    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_insurance")
    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_total_tax_credit")
    util.delete_unused(cr, "l10n_lu_hr_payroll.hr_salary_rule_category_cotisation_base")

    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport_without_VAT")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport_VAT")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_vpa")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_gross_tmp")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_cotisation_base")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_transport_fees")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_total_deduction")
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.l10n_lu_employees{_employee,}_cis"))
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.l10n_lu_employees{_employee,}_ci_co2"))
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_total_tax_credit")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_employee_tax_credit")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_gratification")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_gratification_net_gratification")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_gross_meal_vouchers_2")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport_without_VAT_2")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_atn_transport_VAT_2")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_benefit_various_2")
    util.delete_unused(cr, "l10n_lu_hr_payroll.l10n_lu_employees_net_to_pay")

    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.report_payslip_lux_{thirteen_month,gratification}"))
    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.report_payslip_lux_lang_{thirteen_month,gratification}"))

    util.rename_field(cr, "hr.employee", "l10n_lu_tax_card_number", "l10n_lu_tax_id_number")
    util.rename_field(cr, "hr.employee", "l10n_lu_travel_expense", "l10n_lu_deduction_fd_daily")
    util.remove_field(cr, "hr.contract", "l10n_lu_13th_month")
    util.remove_field(cr, "hr.contract", "l10n_lu_extra_holidays")
    util.remove_field(cr, "hr.contract", "l10n_lu_benefit_in_kind")
    util.rename_field(cr, "hr.contract", "l10n_lu_atn_transport", "l10n_lu_bik_vehicle")
    util.remove_field(cr, "hr.contract", "l10n_lu_wage_with_sacrifices")

    cr.execute("UPDATE hr_employee SET l10n_lu_deduction_fd_daily = l10n_lu_deduction_fd_daily / 25")

    util.rename_xmlid(cr, *eb("l10n_lu_hr_payroll.rule_parameter_cissm_max_amount_{2023,2019}"))
