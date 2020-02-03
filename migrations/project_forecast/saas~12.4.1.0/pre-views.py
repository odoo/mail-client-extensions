# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("project_forecast.project_forecast_action_view_by_user{,_grid}"))
    util.rename_xmlid(cr, *eb("project_forecast.project_forecast_action_view_by_project{,_grid}"))

    util.remove_record(cr, "project_forecast.project_forecast_action_server_by_user")
    util.remove_record(cr, "project_forecast.project_forecast_action_server_by_project")

    util.remove_record(cr, "project_forecast.project_forecast_action_view_grid_from_project")
    util.remove_record(cr, "project_forecast.project_forecast_action_from_project")
