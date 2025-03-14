from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_record(cr, "hr_timesheet.access_project_task")
    util.rename_xmlid(cr, *eb("hr_timesheet.portal_my_task_{planned,allocated}_hours_template"))
    util.rename_field(cr, "report.project.task.user", "planned_hours", "allocated_hours")
    util.remove_view(cr, "hr_timesheet.hr_timesheet_line_search_base")
