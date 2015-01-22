# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""UPDATE account_payment_term_line
                     SET value_amount = coalesce(value_amount, 1) * 100.0
               """)
