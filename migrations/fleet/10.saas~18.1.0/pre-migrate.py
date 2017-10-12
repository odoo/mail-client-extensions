# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE fleet_vehicle_log_contract
           SET state='expired'
         WHERE state='toclose'
    """)

    cr.execute("UPDATE fleet_service_type SET category='service' WHERE id=%s",
               [util.ref(cr, 'fleet.type_contract_repairing')])

    cr.execute("""
        UPDATE fleet_service_type t
           SET category='service'
         WHERE category='both'
           AND EXISTS(SELECT id FROM fleet_vehicle_cost WHERE cost_subtype_id = t.id AND contract_id IS NULL)
           AND NOT EXISTS(SELECT id FROM fleet_vehicle_cost WHERE cost_subtype_id = t.id AND contract_id IS NOT NULL)
    """)
    cr.execute("""
        UPDATE fleet_service_type t
           SET category='contract'
         WHERE category='both'
           AND NOT EXISTS(SELECT id FROM fleet_vehicle_cost WHERE cost_subtype_id = t.id AND contract_id IS NULL)
           AND EXISTS(SELECT id FROM fleet_vehicle_cost WHERE cost_subtype_id = t.id AND contract_id IS NOT NULL)
    """)
    # types in `both` category will be duplicated in `post` script
