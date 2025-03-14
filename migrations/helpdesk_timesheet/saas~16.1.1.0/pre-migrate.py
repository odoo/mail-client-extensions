from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.timesheet_view_grid_by_task_readonly")
