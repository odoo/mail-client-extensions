# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE payment_transaction
           SET callback_model_id = (SELECT id FROM ir_model WHERE model='sale.subscription'),
               callback_method = 'reconcile_pending_transaction',
               callback_res_id = (regexp_matches(callback_eval, '\d+'))[1]::integer
         WHERE callback_eval LIKE 'self.env[''sale.subscription''].reconcile\_pending\_transaction(%'
    """)
