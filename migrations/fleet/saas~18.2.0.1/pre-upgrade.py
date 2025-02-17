from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr,
        "fleet_vehicle_log_services",
        "model_id",
        "integer",
        fk_table="fleet_vehicle_model",
        on_delete_action="SET NULL",
    )
    util.create_column(
        cr,
        "fleet_vehicle_log_services",
        "brand_id",
        "integer",
        fk_table="fleet_vehicle_model_brand",
        on_delete_action="SET NULL",
    )

    query = """
        UPDATE fleet_vehicle_log_services s
           SET model_id = m.id,
               brand_id = m.brand_id
          FROM fleet_vehicle v
          JOIN fleet_vehicle_model m
            ON m.id = v.model_id
         WHERE v.id = s.vehicle_id
    """
    util.explode_execute(cr, query, table="fleet_vehicle_log_services", alias="s")

    util.create_column(
        cr, "fleet_vehicle_odometer", "driver_id", "integer", fk_table="res_partner", on_delete_action="SET NULL"
    )
    query = """
        UPDATE fleet_vehicle_odometer o
           SET driver_id = v.driver_id
          FROM fleet_vehicle v
         WHERE v.id = o.vehicle_id
           AND v.driver_id IS NOT NULL
           AND o.driver_id IS NULL
    """

    util.explode_execute(cr, query, table="fleet_vehicle_odometer", alias="o")
