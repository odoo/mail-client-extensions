# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    env = util.env(cr)

    for warehouse in env['stock.warehouse'].search([]):
        picking_type_vals = warehouse._create_or_update_sequences_and_picking_types()
        if picking_type_vals:
            warehouse.write(picking_type_vals)
        route_vals = warehouse._create_or_update_route()
        if route_vals:
            warehouse.write(route_vals)
