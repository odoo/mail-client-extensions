# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # remove relation to module im_odoo_support
    cr.execute("DELETE FROM openerp_enterprise_database_app WHERE module_id = 444")

    # cleanup bad/duplicated attendance entries
    cr.execute("""
        DELETE FROM hr_attendance WHERE id IN (
            15152, 15153, 15154,            -- duplicated (no check_out)
            23479, 23483, 23898, 23899,     -- duplicated entries (same check_in date)
            1396, 10513, 12899,             -- extra check_in which generate overlaps
            10001                           -- extra check_in from jan 2012
        )
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
