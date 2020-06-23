# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE sale_subscription s
           SET stage_category = t.category
          FROM sale_subscription_stage t
         WHERE t.id = s.stage_id
    """
    )

    util.recompute_fields(cr, "sale.subscription.line", ["price_subtotal", "price_tax", "price_total"])

    cr.execute(
        """
        WITH sums AS (
            SELECT analytic_account_id, SUM(price_subtotal) as untaxed, SUM(price_tax) as tax
              FROM sale_subscription_line
          GROUP BY analytic_account_id
        )
        UPDATE sale_subscription s
           SET recurring_total = sums.untaxed,
               recurring_tax = sums.tax,
               recurring_total_incl = sums.untaxed + sums.tax
          FROM sums
         WHERE s.id = sums.analytic_account_id
    """
    )

    util.recompute_fields(cr, "sale.subscription.log", ["amount_company_currency"])
