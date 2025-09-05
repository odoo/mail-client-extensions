from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_holidays_attendance.hr_leave_allocation_overtime_action")
    util.remove_field(cr, "res.users", "request_overtime")

    util.remove_view(cr, "hr_holidays_attendance.res_users_view_form")
    util.remove_view(cr, "hr_holidays_attendance.hr_leave_allocation_overtime_view_form")

    util.remove_field(cr, "hr.leave", "overtime_id")
    util.remove_field(cr, "hr.leave.allocation", "overtime_id")
