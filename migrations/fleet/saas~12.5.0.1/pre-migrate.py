def migrate(cr, latest_version):
    cr.execute(
        """
            UPDATE fleet_vehicle_cost AS cost
               SET company_id = vehicle.company_id
              FROM fleet_vehicle AS vehicle
             WHERE vehicle.id = cost.vehicle_id
               AND vehicle.company_id IS DISTINCT FROM cost.company_id
        """
    )
