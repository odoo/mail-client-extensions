from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "hr_timesheet_attendance.hr_timesheet_attendance_report_view_tree")
    util.remove_field(cr, "hr.timesheet.attendance.report", "user_id")
