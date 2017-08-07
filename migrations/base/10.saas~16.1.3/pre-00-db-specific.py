# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _db_openerp(cr, version):
    # drop materialized view used by odo for reporting (will be recreated in end- script)
    cr.execute("DROP MATERIALIZED VIEW IF EXISTS usd_rate")

    # force required values
    cr.execute("""
        WITH lines AS (
            SELECT l.id, coalesce(t.name, '/') as name
              FROM account_analytic_line l
         LEFT JOIN product_product p on (p.id=l.product_id)
         LEFT JOIN product_template t on (t.id=p.product_tmpl_id)
             WHERE l.name IS NULL
        )
        UPDATE account_analytic_line l
           SET name = lines.name
          FROM lines
         WHERE lines.id = l.id
    """)
    cr.execute("UPDATE account_voucher_line SET name = '/' WHERE name IS NULL")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {
        '8851207e-1ff9-11e0-a147-001cc0f2115e': _db_openerp,
    })
