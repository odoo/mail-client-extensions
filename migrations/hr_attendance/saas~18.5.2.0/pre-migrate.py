from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_attendance.hr_attendance_validated_hours_employee_simple_tree_view")

    util.remove_field(cr, "res.users", "attendance_state")
    util.remove_field(cr, "res.users", "last_check_in")
    util.remove_field(cr, "res.users", "last_check_out")
