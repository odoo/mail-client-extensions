# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.column_exists(cr, "payment_transaction", "account_invoice_id"):
        cr.execute("""
            INSERT INTO account_invoice_transaction_rel(invoice_id, transaction_id)
                 SELECT account_invoice_id, id
                   FROM payment_transaction
                  WHERE account_invoice_id IS NOT NULL
        """)
