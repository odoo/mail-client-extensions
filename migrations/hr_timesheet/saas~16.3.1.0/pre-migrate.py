from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "timesheet_count")
    util.remove_record(cr, "hr_timesheet.act_hr_timesheet_line_view_pivot")
    util.remove_record(cr, "hr_timesheet.act_hr_timesheet_line_view_graph")

    util.remove_view(cr, "hr_timesheet.report_project_task_user_view_tree")
