# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE delivery_carrier
           SET usps_container = 'VARIABLE'
         WHERE usps_container = 'Regular'
    """)
