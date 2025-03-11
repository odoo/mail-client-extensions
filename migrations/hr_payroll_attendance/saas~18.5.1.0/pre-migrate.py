from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_payroll_attendance.rule_parameter_overtime_pay")
    util.remove_record(cr, "hr_payroll_attendance.rule_parameter_overtime_pay_value")
