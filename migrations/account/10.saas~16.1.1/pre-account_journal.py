# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE account_journal
           SET bank_statements_source = 'undefined'
         WHERE bank_statements_source = 'no_feeds'
    """)
