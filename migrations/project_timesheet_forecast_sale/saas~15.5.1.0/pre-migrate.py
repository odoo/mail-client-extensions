# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "order_line_id")
    util.remove_field(cr, "project.timesheet.forecast.report.analysis", "sale_order_id")
    util.remove_field(cr, "project.timesheet.forecast.report.analysis", "sale_line_id")
    util.remove_view(cr, "project_timesheet_forecast_sale.project_timesheet_forecast_sale_report_view_search")
    util.remove_view(cr, "project_timesheet_forecast_sale.project_timesheet_forecast_sale_report_view_pivot")
    util.remove_view(cr, "project_timesheet_forecast_sale.project_project_view_form")
