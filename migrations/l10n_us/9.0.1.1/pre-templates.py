# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""UPDATE ir_model_data
                     SET noupdate = false
                   WHERE module = 'l10n_us'
                     AND noupdate = true
                     AND model IN ('account.account.template', 'account.fiscal.position.template', 'account.tax.template')
               """)
