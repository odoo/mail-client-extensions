from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_attendance.hr_attendance_validated_hours_employee_simple_tree_view")
    util.remove_view(cr, "hr_attendance.hr_user_view_form")

    util.remove_field(cr, "res.users", "attendance_state")
    util.remove_field(cr, "res.users", "last_check_in")
    util.remove_field(cr, "res.users", "last_check_out")
    util.remove_field(cr, "res.users", "hours_last_month")
    util.remove_field(cr, "res.users", "hours_last_month_display")
    util.remove_field(cr, "res.users", "total_overtime")
    util.remove_field(cr, "res.users", "hours_last_month_overtime")
    util.remove_field(cr, "res.users", "attendance_manager_id")
    util.remove_field(cr, "res.users", "display_extra_hours")
