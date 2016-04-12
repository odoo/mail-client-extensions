# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE delivery_carrier
           SET prod_environment=false
         WHERE temando_test_mode=true
           AND delivery_type='temando'
    """)
