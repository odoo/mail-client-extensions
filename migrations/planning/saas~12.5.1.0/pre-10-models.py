# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Being a fresh module, we cannot trust `version`. Get version of `project_forecast` module
    cr.execute("SELECT latest_version FROM ir_module_module WHERE name = 'project_forecast'")
    version = cr.fetchone()[0]
    pv = util.parse_version
    if pv(version) < pv("saas~12.4"):
        project_forecast = util.import_script("project_forecast/saas~12.4.1.0/pre-migrate.py")
        project_forecast.upgrade(cr)

    util.move_model(cr, "project.forecast", "project_forecast", "planning")
    util.rename_model(cr, "project.forecast", "planning.slot")
    util.move_field_to_module(cr, "planning.slot", "project_id", "planning", "project_forecast")
    util.move_field_to_module(cr, "planning.slot", "task_id", "planning", "project_forecast")
    util.remove_field(cr, "planning.slot", "active")
    util.remove_field(cr, "planning.slot", "stage_id")
    util.remove_field(cr, "planning.slot", "tag_ids")
    util.remove_field(cr, "planning.slot", "project_is_follower")
    util.remove_field(cr, "planning.slot", "time")
    util.remove_field(cr, "planning.slot", "exclude")
    util.remove_field(cr, "planning.slot", "resource_hours")
    util.remove_field(cr, "planning.slot", "resource_time")

    if util.table_exists(cr, "project_forecast_recurrency"):
        util.move_model(cr, "project.forecast.recurrency", "project_forecast", "planning")
        util.rename_model(cr, "project.forecast.recurrency", "planning.recurrency")

        util.rename_field(cr, "planning.recurrency", "forecast_ids", "slot_ids")
