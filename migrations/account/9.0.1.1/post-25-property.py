# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    props = util.splitlines("""
        # res.partner
        account_payable
        account_receivable
        account_position
        payment_term
        supplier_payment_term

        # product.category
        account_income_categ
        account_expense_categ

        # product.template
        account_income
        account_expense
    """)
    for p in props:
        util.rename_field(cr, 'property_%s' % p, 'property_%s_id' % p)
