# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_account
           SET reconcile = true
         WHERE internal_type IN ('payable', 'receivable')
           AND reconcile = false
    """
    )
