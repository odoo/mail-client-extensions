# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr, "fleet.vehicle.model", "default_fuel_type", {"hybrid": "full_hybrid", "full_hybrid_gasoline": "full_hybrid"}
    )
    util.change_field_selection_values(
        cr, "fleet.vehicle", "fuel_type", {"hybrid": "full_hybrid", "full_hybrid_gasoline": "full_hybrid"}
    )

    util.create_column(cr, "fleet_vehicle", "category_id", "integer")
    query = """
        UPDATE fleet_vehicle v
           SET category_id = m.category_id
          FROM fleet_vehicle_model m
         WHERE m.id = v.model_id
           AND m.category_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="fleet_vehicle", alias="v"))
