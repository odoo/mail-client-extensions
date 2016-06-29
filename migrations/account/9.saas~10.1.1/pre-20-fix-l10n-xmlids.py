# -*- coding: utf-8 -*-

def migrate(cr, version):
    # don't know why, but some databases have the tracking xmlids created in noupdate=false
    cr.execute(r"""
        UPDATE ir_model_data
           SET noupdate=true
         WHERE module like 'l10n\_%'
           AND model IN ('account.account',
                         'account.fiscal.position',
                         'account.fiscal.position.tax',
                         'account.fiscal.position.account',
                         'account.tax')
    """)
