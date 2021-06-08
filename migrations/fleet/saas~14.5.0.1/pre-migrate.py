# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "fleet_vehicle_model", "category_id", "int4")
    util.create_column(cr, "fleet_vehicle_model", "transmission", "varchar")

    util.create_column(cr, "fleet_vehicle", "trailer_hook", "bool", default=False)

    util.create_column(cr, "fleet_vehicle", "fleet_id", "integer")

    util.create_column(cr, "fleet_vehicle_model", "model_year", "int4")
    util.create_column(cr, "fleet_vehicle_model", "color", "varchar")
    util.create_column(cr, "fleet_vehicle_model", "seats", "int4")
    util.create_column(cr, "fleet_vehicle_model", "doors", "int4")
    util.create_column(cr, "fleet_vehicle_model", "trailer_hook", "bool", default=False)
    util.move_field_to_module(cr, "fleet.vehicle.model", "default_co2", "l10n_be_hr_payroll_fleet", "fleet")
    util.create_column(cr, "fleet_vehicle_model", "co2_standard", "varchar")
    util.move_field_to_module(cr, "fleet.vehicle.model", "default_fuel_type", "l10n_be_hr_payroll_fleet", "fleet")
    util.create_column(cr, "fleet_vehicle_model", "power", "int4")
    util.create_column(cr, "fleet_vehicle_model", "horsepower", "int4")
    util.create_column(cr, "fleet_vehicle_model", "horsepower_tax", "float")
    util.create_column(cr, "fleet_vehicle_model", "electric_assistance", "bool", default=False)

    util.create_column(cr, "fleet_vehicle", "co2_standard", "varchar")
