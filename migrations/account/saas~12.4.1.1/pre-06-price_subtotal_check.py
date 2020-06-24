# -*- encoding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT COUNT(l.id), array_agg(l.id)
          FROM account_invoice_line l
          JOIN account_invoice inv ON inv.id = l.invoice_id
          JOIN res_currency c ON c.id = inv.currency_id
         WHERE l.price_subtotal = 0
           AND ROUND(
                   ABS(l.quantity * (l.price_unit * (1 - COALESCE(l.discount, 0) / 100.0))),
                   (LOG(c.rounding) * -1)::int
               ) > 0
           AND inv.state NOT IN ('open', 'in_payment', 'paid')
        """
    )
    line_count, line_ids = cr.fetchone()

    if line_count:
        raise util.MigrationError(
            "%s invoice lines have an invalid 'price_subtotal' value in pre-migration database."
            "Please investigate and fix it in pre-migration db."
            "Invoice lines ids: (%s)" % (line_count, ", ".join([str(r) for r in line_ids]))
        )
