# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.move_field_to_module(cr, "project.project", "analytic_account_id", "hr_timesheet", "project")
    util.rename_xmlid(cr, *eb("{hr_timesheet,project}.account_analytic_account_view_form_inherit"))
    util.move_field_to_module(cr, "account.analytic.account", "project_ids", "hr_timesheet", "project")
    util.move_field_to_module(cr, "account.analytic.account", "project_count", "hr_timesheet", "project")

    util.remove_field(cr, "project.task", "notes")
