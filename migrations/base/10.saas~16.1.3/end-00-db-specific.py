# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # recreate materialized view used by odo for reporting
    cr.execute("""
        CREATE MATERIALIZED VIEW usd_rate AS (
         SELECT r.currency_id,
            COALESCE(r.company_id, c.id) AS company_id,
            r.rate,
            r.name AS date_start,
            ( SELECT r2.name
                   FROM res_currency_rate r2
                  WHERE r2.name > r.name
                    AND r2.currency_id = r.currency_id
                    AND (r2.company_id IS NULL OR r2.company_id = r.company_id)
                  ORDER BY r2.name
                 LIMIT 1) AS date_stop
           FROM res_currency_rate r
             JOIN res_company c ON r.company_id IS NULL OR r.company_id = c.id
          WHERE r.company_id = 1 AND r.currency_id = 2
        )
    """)

def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
