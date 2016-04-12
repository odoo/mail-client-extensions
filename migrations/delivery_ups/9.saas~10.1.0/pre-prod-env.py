# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE delivery_carrier
           SET prod_environment=false
         WHERE ups_test_mode=true
           AND delivery_type='ups'
    """)
