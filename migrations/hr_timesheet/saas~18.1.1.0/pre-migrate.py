from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "report.project.task.user", "total_hours_spent")
    util.remove_field(cr, "report.project.task.user", "subtask_effective_hours")
