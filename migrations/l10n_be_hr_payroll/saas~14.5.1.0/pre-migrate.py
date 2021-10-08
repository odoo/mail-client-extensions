# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.payslip", "has_attachment_salary")
    util.remove_field(cr, "hr.contract", "attachment_salary_ids")
    util.remove_field(cr, "hr.contract.history", "attachment_salary_ids")

    util.remove_view(cr, "l10n_be_hr_payroll.ll10n_be_attachment_salary_report_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.l10n_be_attachment_salary_report_view_pivot")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_search")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_tree")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_view_form")

    util.remove_record(cr, "l10n_be_hr_payroll.ir_rule_attachment_salary_report_multi_company")

    util.remove_model(cr, "l10n_be.attachment.salary")
    util.remove_model(cr, "l10n_be.attachment.salary.report")

    util.create_column(cr, "hr_employee", "l10n_be_dependent_children_attachment", "int4")

    util.create_column(cr, "res_company", "l10n_be_ffe_employer_type", "varchar", default="commercial")

    util.remove_model(cr, "l10n_be.hr.payroll.credit.time.wizard")
    util.remove_model(cr, "l10n_be.hr.payroll.exit.credit.time.wizard")

    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_employees_salary_attachment_salary")
    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_employees_salary_asignment_salary")
    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_employees_salary_child_support")

    for year, val in [("2018", "1609.47"), ("2019", "1641.62"), ("2020", "1674.49"), ("2021", "1707.94")]:
        util.ensure_xmlid_match_record(
            cr,
            f"l10n_be_hr_payroll.rule_parameter_value_work_bonus_reference_wage_low_{year}",
            "hr.rule.parameter.value",
            {"parameter_value": val},
        )
    for year, val in [("2018", "2510.47"), ("2019", "2560.57"), ("2020", "2611.78"), ("2021", "2664.08")]:
        util.ensure_xmlid_match_record(
            cr,
            f"l10n_be_hr_payroll.rule_parameter_value_work_bonus_reference_wage_high_{year}",
            "hr.rule.parameter.value",
            {"parameter_value": val},
        )
    for year, val in [("2018", "197.67"), ("2019", "201.62"), ("2020", "205.65"), ("2021", "209.76")]:
        util.ensure_xmlid_match_record(
            cr,
            f"l10n_be_hr_payroll.rule_parameter_value_work_bonus_basic_amount_{year}",
            "hr.rule.parameter.value",
            {"parameter_value": val},
        )
    for year, val in [("2018", "31320"), ("2019", "31990"), ("2020", "32640")]:
        util.ensure_xmlid_match_record(
            cr,
            f"l10n_be_hr_payroll.rule_parameter_ip_second_bracket_{year}",
            "hr.rule.parameter.value",
            {"parameter_value": val},
        )

    for record in [
        "hr_payroll.hr_salary_rule_salary_attachment",
        "hr_payroll.hr_salary_rule_salary_assignment",
        "hr_payroll.hr_salary_rule_child_support",
        "l10n_be_hr_payroll.cp200_employees_double_holiday_salary_attachment_salary",
        "l10n_be_hr_payroll.cp200_employees_double_holiday_salary_asignment_salary",
        "l10n_be_hr_payroll.cp200_employees_double_holiday_salary_child_support",
        "l10n_be_hr_payroll.cp200_employees_salary_attachment_salary",
        "l10n_be_hr_payroll.cp200_employees_salary_asignment_salary",
        "l10n_be_hr_payroll.cp200_employees_salary_child_support",
        "l10n_be_hr_payroll.cp200_employees_termination_n1_attachment_salary",
        "l10n_be_hr_payroll.cp200_employees_termination_n1_asignment_salary",
        "l10n_be_hr_payroll.cp200_employees_termination_n1_child_support",
        "l10n_be_hr_payroll.cp200_employees_termination_n_attachment_salary",
        "l10n_be_hr_payroll.cp200_employees_termination_n_asignment_salary",
        "l10n_be_hr_payroll.cp200_employees_termination_n_child_support",
        "l10n_be_hr_payroll.cp200_employees_thirteen_month_salary_attachment_salary",
        "l10n_be_hr_payroll.cp200_employees_thirteen_month_salary_asignment_salary",
        "l10n_be_hr_payroll.cp200_employees_thirteen_month_salary_child_support",
    ]:
        if not util.delete_unused(cr, record):
            util.force_noupdate(cr, record)
