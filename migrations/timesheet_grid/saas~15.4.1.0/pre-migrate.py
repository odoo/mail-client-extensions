# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for report_type in ["employee", "project", "task"]:
        util.remove_record(cr, f"timesheet_grid.timesheet_action_view_report_by_{report_type}_grid")
