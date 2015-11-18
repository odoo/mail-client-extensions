# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    update_table = [
        ('receivable', util.ref(cr, 'account.data_account_type_receivable')),
        ('payable', util.ref(cr, 'account.data_account_type_payable')),
    ]

    util.create_column(cr, 'account_account_type', 'include_initial_balance', 'bool')
    util.create_column(cr, 'account_account_type', 'type', 'varchar')

    for entry in update_table:
        cr.execute("""UPDATE account_account_type
            SET include_initial_balance = true, type = %s
            WHERE id = %s
            """, (entry[0], entry[1]))

    util.create_column(cr, 'account_account', 'reconcile', 'bool')

    cr.execute("""UPDATE account_account
        SET reconcile = true
        WHERE user_type IN %s
        """, ((util.ref(cr, 'account.data_account_type_receivable'), util.ref(cr, 'account.data_account_type_payable')),))
