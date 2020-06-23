# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def _db_openerp(cr, version):
    util.create_column(cr, "fleet_vehicle_log_services", "description", "text")
    cr.execute("""UPDATE fleet_vehicle_log_services fvls
                  SET description = fvc.description
                  FROM fleet_vehicle_cost fvc
                  WHERE fvc.id = fvls.cost_id""")
    util.rename_field(cr, "fleet.vehicle.log.services", "description", "description_keep")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
