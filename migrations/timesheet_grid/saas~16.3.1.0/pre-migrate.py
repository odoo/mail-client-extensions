# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.analytic.line", "can_edit")
    util.remove_view(cr, "timesheet_grid.timesheet_grid_pivot_view_weekly_validate")
    util.remove_record(cr, "timesheet_grid.hr_timesheet_to_validate_action_pivot")
    util.remove_record(cr, "timesheet_grid.hr_timesheet_to_validate_action_graph")
