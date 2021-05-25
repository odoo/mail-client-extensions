# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(
        cr, "res.company", "leave_timesheet_project_id", "project_timesheet_holidays", "hr_timesheet"
    )
    util.rename_field(cr, "res.company", "leave_timesheet_project_id", "internal_project_id")
    util.create_column(cr, "res_company", "internal_project_id", "int4")
