# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "plan_to_change_bike", "bool", default=False)
    util.create_column(cr, "fleet_vehicle", "plan_to_change_bike", "bool")
    util.create_column(cr, "fleet_vehicle", "frame_type", "varchar")
    util.create_column(cr, "fleet_vehicle", "electric_assistance", "bool")
    util.create_column(cr, "fleet_vehicle", "frame_size", "float8")

    cr.execute("UPDATE res_partner SET plan_to_change_car=False")
    cr.execute("UPDATE fleet_vehicle SET plan_to_change_car=False")

    cr.execute("SELECT res_id FROM ir_model_data WHERE name='fleet_vehicle_state_waiting_list'")
    row = cr.fetchone()
    res_id = row[0] if row else -1

    vehicle_field = [("bike", "plan_to_change_bike"), ("car", "plan_to_change_car")]
    for (vehicule_type, field_to_update) in vehicle_field:
        cr.execute(
            f"""
            WITH f AS (
                SELECT future_driver_id, vehicle_type
                FROM fleet_vehicle
                JOIN fleet_vehicle_model ON fleet_vehicle.model_id=fleet_vehicle_model.id
                WHERE future_driver_id is not null AND vehicle_type=%s AND (state_id IS NULL OR state_id <> %s))
            UPDATE res_partner
            SET {field_to_update}=True
            FROM f
            WHERE res_partner.id=f.future_driver_id;
        """,
            (vehicule_type, res_id),
        )

        cr.execute(
            f"""
            WITH f AS (
                SELECT future_driver_id, vehicle_type
                FROM fleet_vehicle
                JOIN fleet_vehicle_model ON fleet_vehicle.model_id=fleet_vehicle_model.id
                WHERE future_driver_id is not null AND vehicle_type=%s AND (state_id IS NULL OR state_id <> %s))
            UPDATE fleet_vehicle
            SET {field_to_update}=True
            FROM f
            WHERE fleet_vehicle.driver_id=f.future_driver_id;
        """,
            (vehicule_type, res_id),
        )
