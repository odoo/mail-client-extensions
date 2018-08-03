# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

PROJECT_FIELDS = {
    "account.analytic.account": {"uom_company_id", "project_ids", "project_count"},
    "project.project": {"analytic_account_id"},
    "project.task": {"remaining_hours"},
}

PROJECT_XMLIDS = """
    access_account_analytic_account_user
    access_account_analytic_account_manager
    access_account_analytic_account_portal
    access_account_analytic_line_project
"""


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "timesheet_cost", "sale_timesheet", "hr_timesheet")
    util.move_field_to_module(cr, "hr.employee", "currency_id", "sale_timesheet", "hr_timesheet")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_timesheet.access_{product,uom}_uom_hr_timesheet"))

    if util.module_installed(cr, "project"):
        for x in util.splitlines(PROJECT_XMLIDS):
            util.rename_xmlid(cr, "project." + x, "hr_timesheet." + x)
        for model, fields in PROJECT_FIELDS.items():
            for field in fields:
                util.move_field_to_module(cr, model, field, "project", "hr_timesheet")
