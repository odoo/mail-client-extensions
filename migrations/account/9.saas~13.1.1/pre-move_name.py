# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_bank_statement_line', 'move_name', 'varchar')
    cr.execute("""
        WITH to_upd AS (
            SELECT m.name, m.statement_line_id, l.payment_id
              FROM account_move_line l
              JOIN account_move m ON (l.move_id = m.id)
             WHERE l.payment_id IS NOT NULL
               AND m.statement_line_id IS NOT NULL
        ),
        _upd_payment AS (
            UPDATE account_payment p
               SET payment_reference = u.name
              FROM to_upd u
             WHERE p.id = u.payment_id
        ),
        _upd_stmt_line AS (
            UPDATE account_bank_statement_line l
               SET move_name = u.name
              FROM to_upd u
             WHERE l.id = u.statement_line_id
        )
        SELECT 1
    """)

    util.create_column(cr, 'account_payment', 'move_name', 'varchar')
    cr.execute("""
        WITH to_upd AS (
            SELECT l.payment_id, (array_agg(m.name order by m.id))[1] as move_name
              FROM account_move_line l
              JOIN account_move m ON (m.id = l.move_id)
              JOIN account_payment p ON (p.id = l.payment_id)
             WHERE p.payment_type != 'transfer'
          GROUP BY l.payment_id
        )
        UPDATE account_payment p
           SET move_name = u.move_name
          FROM to_upd u
         WHERE p.id = u.payment_id
    """)
