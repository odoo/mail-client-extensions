# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.create_column(cr, 'account_invoice_line', 'asset_mrr', 'numeric')
    util.create_column(cr, 'account_invoice_line', 'asset_start_date', 'date')
    util.create_column(cr, 'account_invoice_line', 'asset_end_date', 'date')

    cr.execute("""
        UPDATE  account_invoice_line l
        SET     asset_mrr =
                    (CASE
                        WHEN i.type in ('out_invoice', 'out_refund')
                        THEN l.price_subtotal_signed / (c.method_number * method_period)
                        ELSE 0
                     END),
                asset_start_date =
                    (CASE
                        WHEN i.date_invoice is not null
                        THEN date_trunc('month',i.date_invoice)::date
                        ELSE null
                     END),
                asset_end_date =
                    (CASE
                        WHEN i.date_invoice is not null
                        THEN date_trunc('month',i.date_invoice)::date + ((c.method_number * method_period) || ' months')::interval - INTERVAL '1 days'
                        ELSE null
                     END)
        FROM    account_invoice i,
                account_asset_category c
        WHERE   l.invoice_id = i.id
        AND     l.asset_category_id = c.id
    """)
