# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT   line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
        FROM     account_move_line line
        JOIN     account_move move ON move.id = line.move_id
        JOIN     account_journal journal ON journal.id = move.journal_id
        JOIN     res_company company ON company.id = journal.company_id
        JOIN     res_currency currency ON currency.id = company.currency_id
        GROUP BY line.move_id, currency.decimal_places
        HAVING   ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        """
    )

    if cr.rowcount:
        moves = ["(id: %s, balance: %s)" % (r[0], r[1]) for r in cr.fetchall()]
        raise util.MigrationError("The following moves are not balanced:\n %s" % '\n'.join(moves))
