# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_invoice_line", 'subscription_start_date', 'timestamp without time zone')
    util.create_column(cr, "account_invoice_line", 'subscription_end_date', 'timestamp without time zone')
    util.create_column(cr, "account_invoice_line", 'subscription_mrr', 'numeric')

    cr.execute("""
        UPDATE account_invoice_line
           SET subscription_start_date=asset_start_date,
               subscription_end_date=asset_end_date
         WHERE subscription_id IS NOT NULL
    """)
