# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'statement_line_id', 'int4')

    cr.execute("""
        UPDATE account_move_line l
           SET statement_line_id = m.statement_line_id
          FROM account_move m
         WHERE m.id = l.move_id
    """)

    util.remove_field(cr, 'account.move', 'statement_line_id')
