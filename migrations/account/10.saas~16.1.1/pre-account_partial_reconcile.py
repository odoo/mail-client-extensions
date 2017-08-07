# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_partial_reconcile', 'max_date', 'date')
    cr.execute("""
        UPDATE account_partial_reconcile p
           SET max_date = GREATEST(d.date, c.date)
          FROM account_move_line c, account_move_line d
         WHERE c.id = p.credit_move_id
           AND d.id = p.debit_move_id
    """)
