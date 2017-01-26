# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # remove relation to module delivery_temando
    cr.execute("""
        DELETE FROM openerp_enterprise_database_app WHERE module_id IN (
            SELECT id FROM ir_module_module WHERE name = 'delivery_temando'
        )
    """)

    # cleanup followers: SUPERUSER does not follow anything
    cr.execute("""
        DELETE FROM mail_followers
              WHERE partner_id = (SELECT partner_id FROM res_users WHERE id = 1)
    """)


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
