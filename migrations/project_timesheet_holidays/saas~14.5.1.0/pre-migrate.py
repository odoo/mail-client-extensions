# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "leave_timesheet_project_id", "internal_project_id")
    util.create_column(cr, "account_analytic_line", "global_leave_id", "int4")
