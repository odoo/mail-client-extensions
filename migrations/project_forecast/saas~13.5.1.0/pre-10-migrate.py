# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_forecast.project_forecast_view_gantt")
    util.remove_view(cr, "project_forecast.project_forecast_view_pivot")
    util.remove_view(cr, "project_forecast.project_forecast_view_graph")
    util.remove_view(cr, "project_forecast.project_forecast_view_grid")
    util.remove_record(cr, "project_forecast.project_forecast_action_analysis")
    util.remove_record(cr, "project_forecast.project_forecast_action_analysis_pivot")
    util.remove_record(cr, "project_forecast.project_forecast_action_analysis_graph")
    util.remove_record(cr, "project_forecast.project_forecast_action_analysis_gantt")
    util.remove_menus(cr, [util.ref(cr, "project_forecast.project_forecast_report_activities")])
