# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    select = " UNION ".join(
        "SELECT {0}, id FROM payment_transaction WHERE {0} IS NOT NULL".format(c)
        for c in ["account_invoice_id", "invoice_id"]
        if util.column_exists(cr, "payment_transaction", c)
    )
    if select:
        cr.execute("INSERT INTO account_invoice_transaction_rel(invoice_id, transaction_id) " + select)
