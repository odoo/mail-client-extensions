# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_transaction
           SET acquirer_reference=buckaroo_txnid
         WHERE buckaroo_txnid IS NOT NULL
    """)

    util.remove_field(cr, 'payment.transation', 'buckaroo_txnid')
    util.remove_view(cr, 'payment_buckaroo.transaction_form_buckaroo')
