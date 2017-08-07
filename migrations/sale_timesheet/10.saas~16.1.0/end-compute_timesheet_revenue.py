# -*- coding: utf-8 -*-
from operator import itemgetter
import logging
from odoo.addons.base.maintenance.migrations import util

NS = 'odoo.addons.base.maintenance.migrations.sale_timesheet.saas-16.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    env = util.env(cr)

    cr.execute("""
        UPDATE account_analytic_line l
           SET timesheet_invoice_type =
             CASE WHEN t.invoice_policy = 'delivery' THEN 'billable_time'
                  WHEN t.invoice_policy = 'order' AND t.track_service = 'task' THEN 'billable_fixed'
                  ELSE NULL
              END
         FROM sale_order_line sol,
              account_analytic_account a,
              product_product p JOIN product_template t ON (p.product_tmpl_id = t.id)
        WHERE sol.id = l.so_line
          AND a.id = l.account_id
          AND p.id = sol.product_id
          AND t.type = 'service'
          AND l.project_id IS NOT NULL
    """)

    cr.execute("""
        UPDATE account_analytic_line
           SET timesheet_invoice_type = 'non_billable',
               timesheet_revenue = 0
         WHERE timesheet_invoice_type IS NULL
    """)

    # compute revenue for line with same currency for account and so
    cr.execute("""
        UPDATE account_analytic_line l
           SET timesheet_revenue =
             CASE WHEN sol.currency_id != a.currency_id THEN NULL
                  ELSE round((l.unit_amount * sol.price_unit * (1 - sol.discount))::numeric,
                             ceil(-log(c.rounding))::integer)
              END
         FROM sale_order_line sol,
              account_analytic_account a,
              res_currency c
        WHERE sol.id = l.so_line
          AND a.id = l.account_id
          AND a.currency_id = c.id
          AND l.timesheet_invoice_type IN ('billable_time', 'billable_fixed')
    """)

    # for billable_fixed, sum should not be greater than the soline total
    cr.execute("""
        SELECT (sol.product_uom_qty * sol.price_unit * (1 - sol.discount)) as total,
               array_agg(l.id ORDER BY l.id),
               array_agg(l.timesheet_revenue::float8 ORDER BY l.id)
          FROM account_analytic_line l
          JOIN sale_order_line sol ON (sol.id = l.so_line)
          JOIN account_analytic_account a ON (a.id = l.account_id)
         WHERE l.timesheet_invoice_type = 'billable_fixed'
           AND sol.currency_id = a.currency_id
      GROUP BY l.so_line, total
        HAVING sum(l.timesheet_revenue) > (sol.product_uom_qty * sol.price_unit * (1 - sol.discount))
    """)
    for total, ids, revenues in cr.fetchall():
        sum_ = 0.0
        for lid, revenue in zip(ids, revenues):
            if sum_ + revenue > total:
                val = max(0, total - sum_)
                cr.execute("UPDATE account_analytic_line SET timesheet_revenue=%s WHERE id=%s",
                           [val, lid])
            sum_ += revenue

    cr.execute("SELECT id FROM account_analytic_line WHERE timesheet_revenue IS NULL ORDER BY id")
    ids = map(itemgetter(0), cr.fetchall())

    AAL = env['account.analytic.line']

    # took about 10 minutes on openerp@next
    for timesheet in util.iter_browse(AAL, ids, logger=_logger, chunk_size=1):
        values = timesheet._get_timesheet_billing_values({})
        values['id'] = timesheet.id
        cr.execute("""
            UPDATE account_analytic_line
               SET timesheet_revenue = %(timesheet_revenue)s,
                   timesheet_invoice_type = %(timesheet_invoice_type)s
             WHERE id=%(id)s
        """, values)

    # link timesheet lines with invoices
    cr.execute("""
        WITH aal AS (
            SELECT r.invoice_line_id
                FROM account_analytic_line l
                JOIN sale_order_line_invoice_rel r ON (r.order_line_id = l.so_line)
               WHERE l.project_id IS NOT NULL
                 AND l.timesheet_invoice_type IN ('billable_time', 'billable_fixed')
        )
        SELECT i.id
          FROM account_invoice_line l
          JOIN account_invoice i ON (i.id = l.invoice_id)
          JOIN product_product p ON (p.id = l.product_id)
          JOIN product_template t ON (t.id = p.product_tmpl_id)
         WHERE i.state IN ('paid', 'open')
           AND t.type = 'service'
           AND t.invoice_policy IN ('delivery', 'order')
           AND EXISTS(SELECT 1 FROM aal WHERE invoice_line_id = l.id)
      GROUP BY i.id
      ORDER BY i.id
    """)

    ids = map(itemgetter(0), cr.fetchall())

    INV = env['account.invoice']

    for invoices in util.iter_browse(INV, ids, logger=_logger):
        invoices._compute_timesheet_revenue()
