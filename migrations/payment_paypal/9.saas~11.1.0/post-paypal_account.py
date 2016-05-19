# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if version:     # FIXME use util.ENVIRON?
        # This script should only be execute on new-install of the module
        return

    main_company = util.ref(cr, 'base.main_company')
    Acquirers = util.env(cr)['payment.acquirer']
    paypal = Acquirers.browse(util.ref(cr, 'payment.payment_acquirer_paypal'))
    cr.execute("SELECT id, paypal_account FROM res_company WHERE paypal_account IS NOT NULL")
    for cid, paypal_account in cr.fetchall():
        if cid == main_company:
            paypal.write({'company_id': cid, 'paypal_email_account': paypal_account})
        else:
            paypal.copy({'company_id': cid, 'paypal_email_account': paypal_account})
