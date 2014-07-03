# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # Even if there was a many2many between statement lines and account move,
    # it must have at most one statement line per move.
    # Fail if we found more.
    cr.execute("""SELECT 1
                    FROM account_bank_statement_line_move_rel
                GROUP BY move_id
                  HAVING count(statement_line_id) > 1
               """)
    if cr.rowcount:
        raise util.MigrationError("More than one bank statement line per move found")

    util.create_column(cr, 'account_bank_statement_line', 'journal_entry_id', 'int4')

    cr.execute("""UPDATE account_bank_statement_line l
                     SET journal_entry_id = m.move_id
                    FROM account_bank_statement_line_move_rel m
                   WHERE m.statement_line_id = l.id
               """)
