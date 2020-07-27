# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle_log_services", "active", "boolean", default=True)
    util.create_column(cr, "fleet_vehicle_log_services", "description", "varchar")
    util.create_column(cr, "fleet_vehicle_log_services", "state", "varchar", default="running")

    util.create_column(cr, "fleet_vehicle_model", "vehicle_type", "varchar", default="car")
