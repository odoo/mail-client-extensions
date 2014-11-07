# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""UPDATE ir_model_data
                     SET noupdate = true
                   WHERE model = 'account.account.type'
                     AND module = 'l10n_ro'
               """)
