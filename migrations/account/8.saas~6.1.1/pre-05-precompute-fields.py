# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_line", "partner_id", "int4")
    util.explode_execute(
        cr,
        """
          UPDATE account_analytic_line l
             SET partner_id = a.partner_id
            FROM account_analytic_account a
           WHERE a.id = l.account_id
        """,
        alias="l",
        table="account_analytic_line",
    )

    # speed up computing price_subtotal_signed + avoid writing on all invoice lines,
    # triggering lots of useless and dangerous re-computations!
    util.create_column(cr, "account_invoice_line", "price_subtotal_signed", "numeric")
    cr.execute("""
        WITH currency_rate (currency_id, rate, date_start, date_end) AS (
            SELECT r.currency_id, r.rate, r.name AS date_start,
                   (SELECT name FROM res_currency_rate r2
                    WHERE r2.name > r.name AND
                          r2.currency_id = r.currency_id
                    ORDER BY r2.name ASC
                    LIMIT 1) AS date_end
            FROM res_currency_rate r
        )
        UPDATE  account_invoice_line l
        SET     price_subtotal_signed =
                    (CASE
                        WHEN i.type in ('in_invoice', 'out_refund')
                        THEN -1
                        ELSE 1
                     END)
                    *
                    (CASE
                        WHEN i.currency_id = c_comp.id
                        THEN l.price_subtotal
                        ELSE round(l.price_subtotal * c_comp_rate.rate / c_inv_rate.rate,
                                   ceil(-log(c_comp.rounding))::integer)
                     END)
        FROM    account_invoice i,
                res_currency c_inv,
                res_company c,
                res_currency c_comp,
                currency_rate c_inv_rate,
                currency_rate c_comp_rate
        WHERE   l.invoice_id = i.id
        AND     i.currency_id = c_inv.id
        AND     i.company_id = c.id
        AND     c.currency_id = c_comp.id
        AND     (c_inv_rate.currency_id = c_inv.id AND
                 c_inv_rate.date_start <= COALESCE(i.date_invoice, NOW()) AND
                 (c_inv_rate.date_end IS NULL OR c_inv_rate.date_end > COALESCE(i.date_invoice, NOW())))
        AND     (c_comp_rate.currency_id = c_comp.id AND
                 c_comp_rate.date_start <= COALESCE(i.date_invoice, NOW()) AND
                 (c_comp_rate.date_end IS NULL OR c_comp_rate.date_end > COALESCE(i.date_invoice, NOW())))
    """)
