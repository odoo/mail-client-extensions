# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "timesheet_count")
    util.remove_record(cr, "hr_timesheet.act_hr_timesheet_line_view_pivot")
    util.remove_record(cr, "hr_timesheet.act_hr_timesheet_line_view_graph")
