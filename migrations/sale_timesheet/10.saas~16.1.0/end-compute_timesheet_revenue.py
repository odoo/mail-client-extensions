# -*- coding: utf-8 -*-
from operator import itemgetter
import logging
from odoo.addons.base.maintenance.migrations import util

NS = 'odoo.addons.base.maintenance.migrations.sale_timesheet.saas-16.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    env = util.env(cr)
    l = _logger.info if version is None else lambda *a: None       # noqa

    if version is None:
        l('Reset timesheet_revenue to 0')
        cr.execute("UPDATE account_analytic_line SET timesheet_revenue=0")

    l('link timesheet_invoice_id')
    cr.execute("""
         UPDATE account_analytic_line A
            SET timesheet_invoice_id = ail.invoice_id
           FROM sale_order_line sol
           JOIN sale_order_line_invoice_rel so_invoice_line ON so_invoice_line.order_line_id = sol.id
           JOIN account_invoice_line ail ON so_invoice_line.invoice_line_id = ail.id
          WHERE A.project_id IS NOT NULL
            AND A.so_line = sol.id
    """)

    l('compute timesheet_invoice_type')
    if util.version_gte('10.saas~18'):
        ts = "t.service_type='timesheet' AND t.service_tracking='task_new_project'"
    else:
        ts = "t.track_service='task'"
    cr.execute("""
        UPDATE account_analytic_line l
           SET timesheet_invoice_type =
             CASE WHEN t.invoice_policy = 'delivery' THEN 'billable_time'
                  WHEN t.invoice_policy = 'order' AND {} THEN 'billable_fixed'
                  ELSE NULL
              END
         FROM sale_order_line sol,
              product_product p JOIN product_template t ON (p.product_tmpl_id = t.id)
        WHERE sol.id = l.so_line
          AND p.id = sol.product_id
          AND t.type = 'service'
          AND l.project_id IS NOT NULL
    """.format(ts))

    cr.execute("""
        UPDATE account_analytic_line
           SET timesheet_invoice_type = 'non_billable',
               timesheet_revenue = 0
         WHERE timesheet_invoice_type IS NULL
    """)

    # compute revenue for line with same currency for account and so
    l('compute revenue')
    cr.execute("""
        UPDATE account_analytic_line l
           SET timesheet_revenue =
             CASE WHEN sol.currency_id != l.currency_id THEN NULL
                  ELSE round((l.unit_amount * sol.price_unit * (1 - (sol.discount / 100)))::numeric,
                             ceil(-log(c.rounding))::integer)
                      / CASE WHEN u_sol.category_id = u_aal.category_id
                             THEN u_sol.factor * u_aal.factor
                             ELSE 1         -- no uom conversion
                         END

              END
         FROM sale_order_line sol,
              res_currency c,
              product_uom u_sol,
              product_uom u_aal
        WHERE sol.id = l.so_line
          AND c.id = l.currency_id
          AND u_sol.id = sol.product_uom
          AND u_aal.id = l.product_uom_id
          AND l.timesheet_invoice_type IN ('billable_time', 'billable_fixed')
    """)

    # for billable_fixed, sum should not be greater than the soline total
    l('avoid revenue > soline total')
    cr.execute("""
        SELECT (sol.product_uom_qty * sol.price_unit * (1 - (sol.discount / 100))) as total,
               array_agg(l.id ORDER BY l.id),
               array_agg(l.timesheet_revenue::float8 ORDER BY l.id)
          FROM account_analytic_line l
          JOIN sale_order_line sol ON (sol.id = l.so_line)
         WHERE l.timesheet_invoice_type = 'billable_fixed'
           AND sol.currency_id = l.currency_id
      GROUP BY l.so_line, total
        HAVING sum(l.timesheet_revenue) > (sol.product_uom_qty * sol.price_unit * (1 - (sol.discount / 100)))
    """)
    for total, ids, revenues in cr.fetchall():
        sum_ = 0.0
        for lid, revenue in zip(ids, revenues):
            if sum_ + revenue > total:
                val = max(0, total - sum_)
                cr.execute("UPDATE account_analytic_line SET timesheet_revenue=%s WHERE id=%s",
                           [val, lid])
            sum_ += revenue

    l('compute revenue for other AAL')
    cr.execute("SELECT id FROM account_analytic_line WHERE timesheet_revenue IS NULL ORDER BY id")
    ids = list(map(itemgetter(0), cr.fetchall()))

    AAL = env['account.analytic.line']

    # took about 10 minutes on openerp@next
    if hasattr(AAL, '_timesheet_compute_theorical_revenue_values'):
        # >= 11 (will fail in saas~18, sorry)
        def get_revenue(timesheet):
            return timesheet._timesheet_compute_theorical_revenue_values()
    else:
        def get_revenue(timesheet):
            return timesheet._get_timesheet_billing_values({})

    for timesheet in util.iter_browse(AAL, ids, logger=_logger, chunk_size=1):
        values = get_revenue(timesheet)

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

    ids = list(map(itemgetter(0), cr.fetchall()))

    INV = env['account.invoice']

    for invoices in util.iter_browse(INV, ids, logger=_logger):
        invoices._compute_timesheet_revenue()


if __name__ == '__main__':
    env = env   # noqa
    migrate(env.cr, None)
    env.cr.commit()
