from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "allocation_count")
    util.remove_field(cr, "res.users", "current_leave_state")
    util.remove_field(cr, "res.users", "leave_manager_id")
    util.remove_field(cr, "res.users", "show_leaves")
    util.remove_field(cr, "res.users", "is_absent")
    util.remove_field(cr, "res.users", "allocation_remaining_display")
    util.remove_field(cr, "res.users", "allocation_display")
    util.remove_field(cr, "res.users", "hr_icon_display")

    util.remove_view(cr, "hr_holidays.res_users_view_form")
