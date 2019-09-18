# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.column_exists(cr, "payment_transaction", "callback_eval"):
        # NOTE: This script is symlinked in website_subscription@saas~17.
        #       If the database is already in saas~15, this script has already been run.
        #       It is also explicitly called in sale_subscription@saas~18.
        #       However, installation of `sale_subscription` doesn't imply the installation
        #       of `payment`.
        return

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
