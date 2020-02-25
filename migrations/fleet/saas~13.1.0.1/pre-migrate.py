# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "fleet.vehicle", "log_fuel")
    util.remove_field(cr, "fleet.vehicle", "cost_count")
    util.remove_field(cr, "fleet.vehicle", "fuel_logs_count")

    util.create_column(cr, "fleet_vehicle", "description", "text")
    util.create_column(cr, "fleet_vehicle", "manager_id", "int4")
    cr.execute(
        """
        UPDATE fleet_vehicle v
           SET manager_id = m.manager_id
          FROM fleet_vehicle_model m
         WHERE m.id = v.model_id
    """
    )

    # Contract Log
    cr.execute("UPDATE fleet_vehicle_log_contract SET state='open' WHERE state='diesoon'")

    cr.execute("ALTER TABLE fleet_vehicle_log_contract ALTER COLUMN name TYPE varchar")
    util.create_column(cr, "fleet_vehicle_log_contract", "vehicle_id", "int4")
    util.create_column(cr, "fleet_vehicle_log_contract", "cost_subtype_id", "int4")
    util.create_column(cr, "fleet_vehicle_log_contract", "amount", "float8")
    util.create_column(cr, "fleet_vehicle_log_contract", "date", "date")
    util.create_column(cr, "fleet_vehicle_log_contract", "company_id", "int4")

    cr.execute(
        """
        UPDATE fleet_vehicle_log_contract l
           SET name = c.name,
               vehicle_id = c.vehicle_id,
               cost_subtype_id = c.cost_subtype_id,
               amount = c.amount,
               date = c.date,
               company_id = c.company_id
          FROM fleet_vehicle_cost c
         WHERE c.id = l.cost_id
    """
    )

    util.remove_column(cr, "fleet_vehicle_log_contract", "purchaser_id")
    for field in {
        "cost_id",
        "generated_cost_ids",
        "sum_cost",
        "cost_amount",
        "cost_type",
        "parent_id",
        "cost_ids",
        "odometer_id",
        "odometer",
        "odometer_unit",
        "contract_id",
        "auto_generated",
        "description",
    }:
        util.remove_field(cr, "fleet.vehicle.log.contract", field)

    # Service
    util.create_column(cr, "fleet_vehicle_log_services", "service_type_id", "int4")
    util.create_column(cr, "fleet_vehicle_log_services", "vehicle_id", "int4")
    util.create_column(cr, "fleet_vehicle_log_services", "amount", "float8")
    util.create_column(cr, "fleet_vehicle_log_services", "odometer_id", "int4")
    util.create_column(cr, "fleet_vehicle_log_services", "date", "date")
    util.create_column(cr, "fleet_vehicle_log_services", "company_id", "int4")

    cr.execute(
        """
        UPDATE fleet_vehicle_log_services s
           SET service_type_id = c.cost_subtype_id,
               vehicle_id = c.vehicle_id,
               amount = c.amount,
               odometer_id = c.odometer_id,
               date = c.date,
               company_id = c.company_id
          FROM fleet_vehicle_cost c
         WHERE c.id = s.cost_id
    """
    )

    util.remove_column(cr, "fleet_vehicle_log_services", "purchaser_id")
    util.rename_field(cr, "fleet.vehicle.log.services", "cost_subtype_id", "service_type_id")
    for field in {
        "cost_id",
        "cost_amount",
        "name",
        "cost_type",
        "parent_id",
        "cost_ids",
        "contract_id",
        "auto_generated",
        "description",
    }:
        util.remove_field(cr, "fleet.vehicle.log.services", field)

    # Model
    util.create_column(cr, "fleet_vehicle_model", "active", "boolean")
    cr.execute("UPDATE fleet_vehicle_model SET active = true")

    # Brand
    util.create_column(cr, "fleet_vehicle_model_brand", "model_count", "int4")
    cr.execute(
        """
        WITH _cnt AS (
            SELECT b.id, count(m.id) as cnt
              FROM fleet_vehicle_model_brand b
         LEFT JOIN fleet_vehicle_model m ON m.brand_id = b.id
          GROUP BY b.id
        )
        UPDATE fleet_vehicle_model_brand b
           SET model_count = c.cnt
          FROM _cnt c
         WHERE c.id = b.id
    """
    )

    # cleanup
    util.remove_model(cr, "fleet.vehicle.log.fuel")
    util.remove_model(cr, "fleet.vehicle.cost")

    menus = util.splitlines(
        """
        menu_fleet_reporting_indicative_costs
        fleet_vehicle_costs_menu
        fleet_vehicle_log_fuel_menu
        fleet_vehicle_model_menu
        fleet_vehicle_contract_types_menu

    """
    )
    util.remove_menus(cr, [util.ref(cr, f"fleet.{menu}") for menu in menus])

    util.remove_record(cr, "fleet.act_renew_contract")
    util.remove_record(cr, "fleet.fleet_vehicle_contract_types_action")
