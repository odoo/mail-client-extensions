# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""update account_payment_term_line set sequence = 20 where value = 'balance'""")
