from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.timesheet.forecast.report.analysis", "task_id")
    util.remove_field(cr, "project.timesheet.forecast.report.analysis", "milestone_id")
