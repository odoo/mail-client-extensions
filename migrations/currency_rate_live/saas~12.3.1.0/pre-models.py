# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE res_company
           SET currency_provider='ecb'
         WHERE currency_provider='yahoo'
    """)
