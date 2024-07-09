from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_in_hr_payroll.action_report_hrsalarybymonth")
    util.remove_view(cr, "l10n_in_hr_payroll.view_salary_employee_month")
    util.remove_view(cr, "l10n_in_hr_payroll.report_hrsalarybymonth")
    util.remove_model(cr, "hr.salary.employee.month")
    util.remove_menus(cr, [util.ref(cr, "l10n_in_hr_payroll.menu_salary_employee_month")])
