# -*- encoding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT COUNT(l.id), array_agg(l.id)
          FROM account_invoice_line l
          JOIN account_invoice inv ON inv.id = l.invoice_id
         WHERE l.price_subtotal = 0
           AND l.price_unit != 0
           AND l.quantity != 0
           AND l.discount != 100
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
