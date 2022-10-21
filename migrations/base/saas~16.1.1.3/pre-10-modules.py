# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "pos_cache")
    util.remove_module(cr, "spreadsheet_dashboard_sale_expense")
    util.remove_module(cr, "association")

    if util.has_enterprise():
        util.remove_module(cr, "project_timesheet_forecast_contract")
        util.remove_module(cr, "event_sale_dashboard")
        util.merge_module(cr, "sale_enterprise", "sale")
