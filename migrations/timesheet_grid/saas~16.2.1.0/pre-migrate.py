from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "timesheet_grid.hr_timesheet_report_search_grid")
