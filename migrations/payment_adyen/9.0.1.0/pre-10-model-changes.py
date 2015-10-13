# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_transaction
           SET acquirer_reference=adyen_psp_reference
         WHERE adyen_psp_reference IS NOT NULL
    """)

    util.remove_field(cr, 'payment.transation', 'adyen_psp_reference')
    util.remove_view(cr, 'payment_adyen.transaction_form_adyen')
