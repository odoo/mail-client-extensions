# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        ALTER TABLE res_company
        ALTER COLUMN phone_international_format
        TYPE varchar
        USING CASE WHEN phone_international_format = true THEN 'prefix' ELSE 'no_prefix' END
    """)
