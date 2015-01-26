# -*- coding: utf-8 -*-
import logging

from openerp.addons.base.maintenance.migrations import util

NS = 'openerp.addons.base.maintenance.migrations.account.saas-6.'
_logger = logging.getLogger(NS + __name__)

def migrate(cr, version):
    cr.execute("""SELECT journal_entry_id, array_agg(id)
                    FROM account_bank_statement_line
                   WHERE journal_entry_id IS NOT NULL
                GROUP BY journal_entry_id
                  HAVING count(id) >= 2
               """)
    if cr.rowcount:
        msg = "Some bank statement lines share the same account move"
        bad_lines = "\n".join("%7s <= %r" % r for r in cr.fetchall())
        _logger.error("%s:\n%s", msg, bad_lines)
        raise util.MigrationError(msg)

    util.create_column(cr, 'account_move', 'statement_line_id', 'int4')
    cr.execute("""UPDATE account_move m
                     SET statement_line_id = l.id
                    FROM account_bank_statement_line l
                   WHERE l.journal_entry_id = m.id
               """)
