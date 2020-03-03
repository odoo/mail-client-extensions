# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute(r"""
        UPDATE ir_model_data
           SET name = 'account_common_' || split_part(name, '_', 2)
         WHERE name ~ '^pgc_\d+_child$'
           AND model = 'account.account.template'
           AND module = 'l10n_es'
    """)
