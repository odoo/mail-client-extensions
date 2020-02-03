# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "project_id", "int4")
    util.create_column(cr, "planning_slot", "task_id", "int4")

    util.remove_field(cr, "res.company", "forecast_generation_span_interval", "int4")
    util.remove_field(cr, "res.company", "forecast_generation_span_uom", "varchar")
    util.remove_field(cr, "res.company", "forecast_default_view", "varchar")
    util.remove_field(cr, "res.config.settings", "forecast_generation_span_interval", "int4")
    util.remove_field(cr, "res.config.settings", "forecast_generation_span_uom", "varchar")
    util.remove_field(cr, "res.config.settings", "forecast_default_view", "varchar")

    util.remove_model(cr, "project.forecast.create")
    util.remove_model(cr, "project.forecast.repeat")

    util.remove_view(cr, "project_forecast.res_config_settings_view_form")
    util.remove_view(cr, "project_forecast.assets_backend")
