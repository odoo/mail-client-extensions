# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # Even if there was a many2many between statement lines and account move,
    # it must have at most one statement line per move.
    # Due to a bug in 7.0, the move was wrongly copied when duplicating a bank statement.
    # We need to keep only the generated move (we discrad the one with the lowest id)

    util.create_column(cr, 'account_bank_statement_line', 'journal_entry_id', 'int4')

    cr.execute("""UPDATE account_bank_statement_line l
                     SET journal_entry_id = m.move_id
                    FROM (SELECT statement_line_id, MAX(move_id) as move_id
                            FROM account_bank_statement_line_move_rel
                           GROUP BY statement_line_id) m
                   WHERE m.statement_line_id = l.id
               """)
