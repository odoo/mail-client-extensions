# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_transaction
           SET acquirer_reference=authorize_txnid
         WHERE authorize_txnid IS NOT NULL
    """)

    util.remove_field(cr, 'payment.transation', 'authorize_txnid')
    util.remove_view(cr, 'payment_authorize.transaction_form_authorize')
