# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.drop_depending_views(cr, "project_forecast", "start_date")
    util.drop_depending_views(cr, "project_forecast", "end_date")
    util.rename_field(cr, "project.forecast", "start_date", "start_datetime")
    util.rename_field(cr, "project.forecast", "end_date", "end_datetime")

    cr.execute("ALTER TABLE project_forecast ALTER COLUMN start_datetime TYPE timestamp without time zone")
    cr.execute(
        """
            ALTER TABLE project_forecast
           ALTER COLUMN end_datetime
                   TYPE timestamp without time zone
                  USING end_datetime + interval '23:59:59'
        """
    )

    util.create_column(cr, "project_forecast", "recurrency_id", "int4")
    util.create_column(cr, "project_forecast", "published", "boolean")
    cr.execute("UPDATE project_forecast SET published = false")

    util.remove_field(cr, "res.company", "forecast_uom")
    util.remove_field(cr, "res.company", "forecast_span")
    util.remove_field(cr, "res.config.settings", "forecast_uom")
    util.remove_field(cr, "res.config.settings", "forecast_span")

    util.create_column(cr, "res_company", "forecast_default_view", "varchar")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("project_forecast.project_forecast_action_view_by_user{,_grid}"))
    util.rename_xmlid(cr, *eb("project_forecast.project_forecast_action_view_by_project{,_grid}"))

    util.remove_record(cr, "project_forecast.project_forecast_action_server_by_user")
    util.remove_record(cr, "project_forecast.project_forecast_action_server_by_project")

    util.remove_record(cr, "project_forecast.project_forecast_action_view_grid_from_project")
    util.remove_record(cr, "project_forecast.project_forecast_action_from_project")
