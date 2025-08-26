from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_view_form")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_average_remunaration_n1")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_average_remunaration_n")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_time_off_n1")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "unpaid_time_off_n")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_allocated")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_taken")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_allocation_n_ids")
    util.remove_field(cr, "hr.payslip.employee.depature.holiday.attests", "time_off_n_ids")
