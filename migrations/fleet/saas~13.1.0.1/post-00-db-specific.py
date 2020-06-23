# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    util.rename_field(cr, "fleet.vehicle.log.services", "description_keep", "description")

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
