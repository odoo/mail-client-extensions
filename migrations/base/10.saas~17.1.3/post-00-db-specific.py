# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = 'odoo.addons.base.maintenance.migrations.base.saas~17.'
_logger = logging.getLogger(NS + __name__)

def _db_openerp(cr, version):
    cr.execute("""
        WITH mods AS (
            SELECT o.id as o, m.id as n
              FROM ir_module_module m
              JOIN ir_module_module o ON (o.name = CONCAT('_', m.name))
             WHERE m.name IN ('account_invoicing', 'sale_management')
        ),
        _up AS (
            UPDATE openerp_enterprise_database_app a
               SET module_id = m.n
              FROM mods m
             WHERE a.module_id = m.o
        )
        DELETE FROM ir_module_module WHERE id IN (SELECT o FROM mods)
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
