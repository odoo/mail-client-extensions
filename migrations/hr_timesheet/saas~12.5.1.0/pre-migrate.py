# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "hr_timesheet.timesheet_rule_portal")
    util.remove_record(cr, "hr_timesheet.access_account_analytic_line_portal")
    util.remove_record(cr, "hr_timesheet.project_task_action_view_timesheet")
