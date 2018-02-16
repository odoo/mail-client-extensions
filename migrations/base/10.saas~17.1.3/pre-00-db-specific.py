# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = 'odoo.addons.base.maintenance.migrations.base.saas~17.'
_logger = logging.getLogger(NS + __name__)

def _db_openerp(cr, version):
    cr.execute("""
        DELETE FROM openerp_enterprise_database_app WHERE module_id IN (
            SELECT id
              FROM ir_module_module
             WHERE name = 'hr_timesheet_sheet'
        )
    """)

    # pre-created module (used by ping) needs to be merged (done in post- script)
    cr.execute("""
        UPDATE ir_module_module
           SET name = concat('_', name)
         WHERE name IN ('account_invoicing', 'sale_management')
    """)

    # cleanup followers: SUPERUSER does not follow anything
    cr.execute("""
        DELETE FROM mail_followers
              WHERE partner_id = (SELECT partner_id FROM res_users WHERE id = 1)
    """)
    _logger.info('cleanup %d follower registration', cr.rowcount)

    cr.execute("""
        DELETE FROM mail_message_res_partner_needaction_rel
              WHERE res_partner_id = (SELECT partner_id FROM res_users WHERE id = 1)
    """)
    _logger.info('cleanup %d needactions', cr.rowcount)

    cr.execute("""
        WITH lines AS (
            SELECT l.id, COALESCE(t.name, '/') as name
              FROM account_analytic_line l
         LEFT JOIN product_product p ON (p.id = l.product_id)
         LEFT JOIN product_template t ON (t.id = p.product_tmpl_id)
             WHERE l.name IS NULL
        )
        UPDATE account_analytic_line l
           SET name = lines.name
          FROM lines
         WHERE lines.id = l.id
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
