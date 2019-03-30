# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

# NOTE
# this script is called multiple time:
# in post- (this script) and in end- to allow depending modules to overwrite values
# it should also be called in post- mrp to allow module `purchase_stock` to be updated
# See #415 #417


def migrate(cr, version):
    env = util.env(cr)

    for warehouse in env["stock.warehouse"].with_context(active_test=False).search([]):
        vals = {'reception_steps': warehouse.reception_steps, 'delivery_steps': warehouse.delivery_steps, 'code': warehouse.code}
        warehouse._create_missing_locations(vals)
        picking_type_vals = warehouse._create_or_update_sequences_and_picking_types()
        if picking_type_vals:
            warehouse.write(picking_type_vals)
        route_vals = warehouse._create_or_update_route()
        if route_vals:
            warehouse.write(route_vals)
        warehouse._create_or_update_global_routes_rules()
