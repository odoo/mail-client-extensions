from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_in_hr_payroll.action_report_hrsalarybymonth")
    util.remove_view(cr, "l10n_in_hr_payroll.view_salary_employee_month")
    util.remove_view(cr, "l10n_in_hr_payroll.report_hrsalarybymonth")
    util.remove_model(cr, "hr.salary.employee.month")
    util.remove_menus(cr, [util.ref(cr, "l10n_in_hr_payroll.menu_salary_employee_month")])

    util.remove_field(cr, "hr.payslip", "advice_id")
    util.remove_field(cr, "hr.payslip.run", "available_advice")

    util.remove_view(cr, "l10n_in_hr_payroll.view_hr_bank_advice_tree")
    util.remove_view(cr, "l10n_in_hr_payroll.view_hr_bank_advice_form")
    util.remove_view(cr, "l10n_in_hr_payroll.view_hr_payroll_advice_filter")
    util.remove_view(cr, "l10n_in_hr_payroll.view_advice_line_form")
    util.remove_view(cr, "l10n_in_hr_payroll.hr_payslip_run_search_inherit")
    util.remove_view(cr, "l10n_in_hr_payroll.hr_payslip_run_form_inherit")

    util.remove_record(cr, "l10n_in_hr_payroll.action_view_hr_bank_advice_tree")
    util.remove_record(cr, "l10n_in_hr_payroll.act_hr_emp_payslip_list")

    util.rename_xmlid(cr, "l10n_in_hr_payroll.payroll_advice", "l10n_in_hr_payroll.payroll_advice_report")
    util.remove_menus(cr, [util.ref(cr, "l10n_in_hr_payroll.action_view_hr_bank_advice_tree")])

    util.remove_model(cr, "hr.payroll.advice")
    util.remove_model(cr, "hr.payroll.advice.line")
    util.remove_model(cr, "report.l10n_in_hr_payroll.report_hrsalarybymonth")

    util.remove_view(cr, "l10n_in_hr_payroll.report_payslipdetails")

    util.remove_field(cr, "yearly.salary.detail", "date_from")
    util.remove_field(cr, "yearly.salary.detail", "date_to")
