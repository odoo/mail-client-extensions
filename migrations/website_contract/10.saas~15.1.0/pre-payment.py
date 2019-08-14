# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute(r"""
        WITH tx AS (
            SELECT id, (regexp_matches(callback_eval, '\d+'))[1]::integer AS res_id
              FROM payment_transaction
             WHERE callback_eval LIKE 'self.env[''sale.subscription''].reconcile\_pending\_transaction(%'
        )
        UPDATE payment_transaction t
           SET callback_model_id = (SELECT id FROM ir_model WHERE model='sale.subscription'),
               callback_method = 'reconcile_pending_transaction',
               callback_res_id = tx.res_id
          FROM tx
         WHERE t.id = tx.id
    """)
