# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_acquirer
           SET save_token = 'always'
         WHERE provider IN ('authorize', 'ogone')
    """)
