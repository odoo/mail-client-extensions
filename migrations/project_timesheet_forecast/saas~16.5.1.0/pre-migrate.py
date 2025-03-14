from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_timesheet_forecast.project_forecast_view_search_inherit_project_timesheet_forecast")
