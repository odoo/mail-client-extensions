# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_timesheet_forecast_sale.timesheet_plan_inherit")
