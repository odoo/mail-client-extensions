# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_timesheet"):
        util.move_field_to_module(cr, "hr.employee", "timesheet_cost", "hr_timesheet", "hr_hourly_cost")
        util.move_field_to_module(cr, "hr.employee", "currency_id", "hr_timesheet", "hr_hourly_cost")
        util.rename_field(cr, "hr.employee", "timesheet_cost", "hourly_cost")
