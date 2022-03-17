# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "plan_to_change_bike", "bool", default=False)
    util.create_column(cr, "fleet_vehicle", "plan_to_change_bike", "bool")
    util.create_column(cr, "fleet_vehicle", "frame_type", "varchar")
    util.create_column(cr, "fleet_vehicle", "electric_assistance", "bool")
    util.create_column(cr, "fleet_vehicle", "frame_size", "float8")
    util.remove_field(cr, "res.config.settings", "module_fleet_account")

    # recompute the fields plan_to_change_{bike,car}
    query = "UPDATE res_partner SET plan_to_change_car = false WHERE plan_to_change_car = true"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner"))
    cr.execute("UPDATE fleet_vehicle SET plan_to_change_car = false WHERE plan_to_change_car = true")

    state_filter = "v.state_id IS NULL"
    waiting_list = util.ref(cr, "fleet.fleet_vehicle_state_waiting_list")
    if waiting_list:
        # as it's a demo data, I expect this branch will only be taken by CI checks
        state_filter = cr.mogrify(f"({state_filter} OR v.state_id = %s)", [waiting_list]).decode()

    cte = f"""\
        cte AS (
            SELECT v.future_driver_id, array_agg(m.vehicle_type) as types
              FROM fleet_vehicle v
              JOIN fleet_vehicle_model m ON v.model_id = m.id
             WHERE v.future_driver_id IS NOT NULL
               AND m.vehicle_type IN ('bike', 'car')
               AND {state_filter}
          GROUP BY v.future_driver_id
        )
    """

    query = f"""
          WITH {cte}
        UPDATE res_partner p
           SET plan_to_change_car = cte.types @> '{{car}}',
               plan_to_change_bike = cte.types @> '{{bike}}'
          FROM cte
         WHERE cte.future_driver_id = p.id
    """
    query = query.replace("{", "{{").replace("}", "}}")
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="res_partner", alias="p"))

    query = f"""
          WITH {cte}
        UPDATE fleet_vehicle v
           SET plan_to_change_car = cte.types @> '{{car}}',
               plan_to_change_bike = cte.types @> '{{bike}}'
          FROM cte
         WHERE cte.future_driver_id = v.driver_id
    """
    cr.execute(query)
