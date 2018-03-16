# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'fleet_vehicle', 'co2_fee', 'float8')
    util.create_column(cr, 'fleet_vehicle', 'total_depreciated_cost', 'float8')

    cr.execute("""
        UPDATE fleet_vehicle
           SET co2_fee = GREATEST(((co2*9.0-600)*1.2488)/12.0, 0)
    """)
    cr.execute("""
        WITH cte AS (
            SELECT v.id, v.co2_fee + SUM(l.recurring_cost_amount_depreciated) as total
              FROM fleet_vehicle_log_contract l
              JOIN fleet_vehicle_cost c ON (c.id = l.cost_id)
              JOIN fleet_vehicle v ON (v.id = c.vehicle_id)
             WHERE l.state = 'open'
          GROUP BY v.id, v.co2_fee
        )
        UPDATE fleet_vehicle v
           SET total_depreciated_cost = cte.total
          FROM cte
         WHERE cte.id = v.id
    """)
    cr.execute("""
        UPDATE fleet_vehicle
           SET total_depreciated_cost = co2_fee
         WHERE total_depreciated_cost IS NULL
    """)
