# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for t in util.env(cr)['fleet.service.type'].search([('category', '=', 'both')]):
        n = t.copy({'category': 'contract'})
        t.write({'cateogory': 'service'})
        cr.execute("""
            UPDATE fleet_vehicle_cost
               SET cost_subtype_id = %s
             WHERE cost_subtype_id = %s
               AND contract_id IS NOT NULL
        """, [n.id, t.id])
