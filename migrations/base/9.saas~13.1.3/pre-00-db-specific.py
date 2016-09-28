# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # remove relation to module im_odoo_support
    cr.execute("DELETE FROM openerp_enterprise_database_app WHERE module_id = 444")

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
