from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_holidays_attendance.hr_employee_view_form")
    util.remove_field(cr, "hr.leave.allocation", "hr_attendance_overtime")
    util.remove_field(cr, "hr.leave.type", "hr_attendance_overtime")
