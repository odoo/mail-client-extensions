# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "timesheet_grid.timesheet_grid_validate_all_timesheets")
