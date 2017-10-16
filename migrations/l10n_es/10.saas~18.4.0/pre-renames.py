# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
           SET name = 'account_common_' || split_part(name, '_', 2)
         WHERE name = 'pgc\_%\_child'
           AND model = 'account.account.template'
           AND module = 'l10n_es'
    """)
