# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'reconcile', 'varchar')

    cr.execute("""UPDATE account_move_line
                     SET reconcile=r.name
                    FROM account_move_reconcile r
                   WHERE reconcile_id = r.id
               """)

    cr.execute("""UPDATE account_move_line l
                     SET reconcile=r.name
                    FROM account_move_reconcile r
                   WHERE l.reconcile_partial_id = r.id
                     AND reconcile IS NOT NULL
               """)
