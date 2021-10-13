# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.account.saas-18."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    env = util.env(cr)
    for name, amount_type, group_by in [
        (
            "invoice lines without python taxes",
            "bool_and(tax.amount_type != 'code')",
            "taxes, price, currency_id, quantity",
        ),
        (
            "invoice lines with python taxes",
            "bool_or(tax.amount_type = 'code')",
            "taxes, price, currency_id, quantity, product_id, partner_id",
        ),
    ]:
        cr.execute(
            """
            WITH lines AS (
                SELECT l.id, array_agg(r.tax_id ORDER BY r.tax_id) as taxes,
                    l.price_unit * (1 - COALESCE(l.discount, 0) / 100.0) as price,
                    i.currency_id, l.quantity, l.product_id, i.partner_id
                FROM account_invoice_line_tax r
                JOIN account_tax tax ON tax.id = r.tax_id
                JOIN account_invoice_line l ON (l.id = r.invoice_line_id)
                JOIN account_invoice i ON (i.id = l.invoice_id)
                WHERE l.price_total IS NULL
            GROUP BY l.id, price, i.currency_id, l.quantity, l.product_id, i.partner_id
            HAVING %(amount_type)s
            )
            SELECT array_agg(id) as line_ids, %(group_by)s
                FROM lines
            GROUP BY %(group_by)s
        """
            % {"amount_type": amount_type, "group_by": group_by}
        )

        size = cr.rowcount
        for row in util.log_progress(cr.dictfetchall(), _logger, qualifier=name, size=size):
            tca = (
                env["account.tax"]
                .browse(row["taxes"])
                .json_friendly_compute_all(
                    row["price"],
                    currency_id=row["currency_id"],
                    quantity=row["quantity"],
                    product_id=row.get("product_id"),
                    partner_id=row.get("partner_id"),
                )
            )
            cr.execute(
                "UPDATE account_invoice_line SET price_total=%s WHERE id IN %s",
                [tca["total_included"], tuple(row["line_ids"])],
            )
            env["account.tax"].invalidate_cache()

    cr.execute("UPDATE account_invoice_line SET price_total=price_subtotal WHERE price_total IS NULL")


if __name__ == "__main__":
    env = env  # noqa: F821
    migrate(env.cr, None)
    env.cr.commit()
