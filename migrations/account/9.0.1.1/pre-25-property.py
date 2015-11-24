# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    prop_map = {
        'res.partner': "account_payable account_receivable account_position payment_term supplier_payment_term".split(),
        'product.category': 'account_income_categ account_expense_categ'.split(),
        'product.template': 'account_income account_expense'.split(),
    }
    for model, props in prop_map.items():
        for p in props:
            util.rename_field(cr, model, 'property_%s' % p, 'property_%s_id' % p)
