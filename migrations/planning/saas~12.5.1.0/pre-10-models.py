# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_model(cr, "project.forecast", "project_forecast", "planning")
    util.rename_model(cr, "project.forecast", "planning.slot")
    util.move_field_to_module(cr, "planning.slot", "project_id", "planning", "project_forecast")
    util.move_field_to_module(cr, "planning.slot", "task_id", "planning", "project_forecast")
    util.remove_field(cr, "planning.slot", "active")
    util.remove_field(cr, "planning.slot", "stage_id")
    util.remove_field(cr, "planning.slot", "tag_ids")
    util.remove_field(cr, "planning.slot", "project_is_follower")
    util.remove_field(cr, "planning.slot", "time")
    util.rename_field(cr, "planning.slot", "published", "is_published")
    util.remove_field(cr, "planning.slot", "exclude")
    util.remove_field(cr, "planning.slot", "resource_hours")
    util.remove_field(cr, "planning.slot", "resource_time")

    if util.table_exists(cr, "project_forecast_recurrency"):
        util.move_model(cr, "project.forecast.recurrency", "project_forecast", "planning")
        util.rename_model(cr, "project.forecast.recurrency", "planning.recurrency")

        util.rename_field(cr, "planning.recurrency", "forecast_ids", "slot_ids")
