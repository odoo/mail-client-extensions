# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.account.saas-18."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    env = util.env(cr)
    cr.execute(
        """
        SELECT l.id, array_agg(r.tax_id) as taxes,
               l.price_unit * (1 - COALESCE(l.discount, 0) / 100.0) as price,
               i.currency_id, l.quantity, l.product_id, i.partner_id
          FROM account_invoice_line_tax r
          JOIN account_invoice_line l ON (l.id = r.invoice_line_id)
          JOIN account_invoice i ON (i.id = l.invoice_id)
         WHERE l.price_total IS NULL
      GROUP BY l.id, price, i.currency_id, l.quantity, l.product_id, i.partner_id
    """
    )

    size = cr.rowcount
    for row in util.log_progress(cr.fetchall(), "invoice lines", _logger, size):
        lid, taxes, price, currency, quantity, product, partner = row

        tca = (
            env["account.tax"]
            .browse(taxes)
            .json_friendly_compute_all(
                price, currency_id=currency, quantity=quantity, product_id=product, partner_id=partner
            )
        )
        cr.execute("UPDATE account_invoice_line SET price_total=%s WHERE id=%s", [tca["total_included"], lid])

    cr.execute("UPDATE account_invoice_line SET price_total=price_subtotal WHERE price_total IS NULL")


if __name__ == "__main__":
    env = env  # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
