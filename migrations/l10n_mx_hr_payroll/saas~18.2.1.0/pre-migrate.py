from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "hr_version"):
        target_model = "hr.version"
    else:
        target_model = "hr.contract"
    util.remove_field(cr, target_model, "l10n_mx_holidays_count")
    util.remove_field(cr, target_model, "l10n_mx_christmas_bonus")
    util.remove_field(cr, target_model, "l10n_mx_risk_bonus_rate")
    util.remove_field(cr, target_model, "l10n_mx_schedule_pay")
    util.rename_field(cr, target_model, "l10n_mx_schedule_pay_temp", "l10n_mx_schedule_pay")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{holiday,l10n_mx_leave}_type_work_risk_imss"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{holiday,l10n_mx_leave}_type_maternity_imss"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{holiday,l10n_mx_leave}_type_disability_due_to_illness_imss"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll_structure_mx_employee_salary,l10n_mx_regular_pay}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{structure_type_employee_mx,l10n_mx_employee}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll_structure_mx_christmas_bonus,l10n_mx_christmas_bonus}"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{structure_type_employee_mx,l10n_mx_employee}"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_days_per_month"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_days_per_month_2000"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_compensation_factor"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_compensation_factor_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_salary_limit_annual_declaration"))
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_l10n_mx_salary_limit_annual_declaration_2024")
    )
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_imss_limit_with_uma"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_imss_limit_with_uma_2016"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_risk_bonus_rate"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_risk_bonus_rate_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_christmas_bonus"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_christmas_bonus_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_christmas_bonus_exemption"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_christmas_bonus_exemption_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_uma"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_uma_2022"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_uma_2023"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_uma_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_uma_2025"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_umi"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_umi_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_daily_minimum_wage"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_daily_minimum_wage_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_daily_minimum_wage_2025"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_exemption_saving_fund_salary"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_exemption_saving_fund_salary_1986"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_exemption_saving_fund_monthly_uma"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_exemption_saving_fund_monthly_uma_2014"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_lower_upper"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_lower_upper_value_2023"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2023"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2025"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2026"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2027"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2028"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2029"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_ceav_percentage_2030"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_isr_table"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_isr_table_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_subsidy_table"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_subsidy_table_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_holiday_table"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_holiday_2024"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_schedule_table"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{,l10n_mx_}rule_parameter_schedule_table_2000"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_provisions"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_integrated_daily_wage"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_social_security_employee"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_social_security_employer"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_social_security_employee_total"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_social_security_employer_total"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_savings_fund_employee"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_savings_fund_employer_alw"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_savings_fund_employer_ded"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_holidays_on_time"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_non_taxable_benefit"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_voucher"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_intermediary_computation"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_exemption"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_taxable_alw"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.{hr_payroll,l10n_mx_category}_taxes"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx{,_work_entry_type}_work_risk_imss"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx{,_work_entry_type}_maternity_imss"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx{,_work_entry_type}_disability_due_to_illness_imss"))

    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_isr"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_subsidy"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_work_risk"))
    util.rename_xmlid(
        cr,
        *eb(
            "l10n_mx_hr_payroll.l10n_mx_{employees_salary_integrated_daily_wage,regular_pay_integrated_daily_wage_base}"
        ),
    )
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_regular_pay_infonavit{,_employee}"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_fixed"))
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_additional")
    )
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_additional_employee")
    )
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_medical")
    )
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_medical_employee")
    )
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_money"))
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disease_maternity_money_employee")
    )
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disability_life"))
    util.rename_xmlid(
        cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_disability_life_employee")
    )
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_retirement"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_ceav"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_ceav_employee"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_imss_nursery"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx_{employees_salary,regular_pay}_infonavit"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx{,_regular_pay}_social_security_total_employee"))
    util.rename_xmlid(cr, *eb("l10n_mx_hr_payroll.l10n_mx{,_regular_pay}_social_security_total_employer"))

    util.remove_view(cr, "l10n_mx_hr_payroll.report_payslip_mx_temp")
    util.delete_unused(
        cr,
        "l10n_mx_hr_payroll.l10n_mx_rule_parameter_subsidy_table_2024",
        "l10n_mx_hr_payroll.l10n_mx_rule_parameter_subsidy_table",
    )
