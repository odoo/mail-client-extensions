# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee", "timesheet_validated")

    util.create_column(cr, "timesheet_validation_line", "project_id", "integer")
    util.create_column(cr, "timesheet_validation_line", "task_id", "integer")
    util.create_m2m(
        cr, "account_analytic_line_timesheet_validation_line_rel", "account_analytic_line", "timesheet_validation_line"
    )

    util.remove_record(cr, "timesheet_grid.hr_timesheet_rule_approver_update")

    # Upgrade view mode as it changed from 'primary' to 'extension'
    view = util.ref(cr, "timesheet_grid.timesheet_view_search")
    if view:
        cr.execute("UPDATE ir_ui_view SET mode='extension' WHERE id=%s", [view])
