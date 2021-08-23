# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle", "driver_employee_id", "int4")
    util.create_column(cr, "fleet_vehicle", "future_driver_employee_id", "int4")

    util.create_column(cr, "fleet_vehicle_assignation_log", "driver_employee_id", "int4")

    util.create_column(cr, "fleet_vehicle_log_services", "purchaser_employee_id", "int4")
