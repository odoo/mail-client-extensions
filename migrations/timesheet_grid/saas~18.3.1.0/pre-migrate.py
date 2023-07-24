from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "project.task.create.timesheet")
    util.remove_field(cr, "project.task", "display_timer_start_secondary")
