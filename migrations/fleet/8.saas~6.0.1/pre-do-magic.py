# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # NOTE oldname is not possible as there is currently a `name` columns
    cr.execute("UPDATE fleet_vehicle_model SET name=modelname")
    util.remove_field(cr, 'fleet.vehicle.model', 'modelname')
