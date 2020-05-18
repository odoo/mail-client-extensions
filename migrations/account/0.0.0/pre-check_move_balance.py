# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    if util.version_gte("saas~11.5"):
        cr.execute(
            """
              SELECT line.move_id,
                     ROUND(SUM(line.debit - line.credit), currency.decimal_places)
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_company company ON company.id = journal.company_id
                JOIN res_currency currency ON currency.id = company.currency_id
               WHERE move.state not in ('draft', 'cancel')
            GROUP BY line.move_id, currency.decimal_places
              HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0
            """
        )
    else:
        cr.execute("SELECT digits FROM decimal_precision WHERE name='account'")
        res = cr.fetchone()
        precision = min(5, res[0]) if res else 2

        cr.execute(
            """
              SELECT line.move_id, ROUND(SUM(line.debit - line.credit), %s)
                FROM account_move_line line
                JOIN account_move move
                  ON (line.move_id = move.id)
               WHERE move.state not in ('draft', 'cancel')
            GROUP BY line.move_id
              HAVING ROUND(SUM(line.debit - line.credit), %s) != 0.0
            """,
            [precision, precision],
        )

    if cr.rowcount:
        if cr.rowcount > 100:
            msg = "A lot of moves are not balanced. You should have a look to that."
        else:
            moves = [f"(id: {id}, balance: {balance})" for id, balance in cr.fetchall()]
            msg = "The following moves are not balanced: [%s]" % ", ".join(moves)

        util.add_to_migration_reports(msg, "Unbalanced Moves")
