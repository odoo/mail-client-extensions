from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave.type", "timesheet_project_id")
    util.remove_field(cr, "hr.leave.type", "timesheet_task_id")
    util.remove_field(cr, "hr.leave.type", "timesheet_generate")
    util.remove_view(cr, "project_timesheet_holidays.hr_holiday_status_view_form_inherit")
