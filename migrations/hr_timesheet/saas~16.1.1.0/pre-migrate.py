from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "reminder_manager_allow", "reminder_allow")
    util.remove_field(cr, "res.config.settings", "timesheet_encode_uom_id")
    util.remove_view(cr, "hr_timesheet.project_sharing_project_task_view_search_inherit_timesheet")
    util.remove_view(cr, "hr_timesheet.project_sharing_inherit_project_task_view_tree")
    util.remove_view(cr, "hr_timesheet.report_project_task_user_view_search")
    util.remove_view(cr, "hr_timesheet.view_task_search_form_hr_extended")
    util.rename_field(cr, "report.project.task.user", "hours_planned", "planned_hours")
    util.rename_field(cr, "report.project.task.user", "hours_effective", "effective_hours")
