# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
         ALTER TABLE pos_config
        ALTER COLUMN iface_tax_included
                TYPE varchar
               USING CASE WHEN iface_tax_included THEN 'total'
                          ELSE 'subtotal'
                      END
    """)
