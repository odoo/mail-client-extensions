# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~11.5"):
        cr.execute(
            """
              SELECT line.move_id,
                     CONCAT(move.name, ', with a balance of ', ROUND(SUM(line.debit - line.credit), currency.decimal_places))
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_company company ON company.id = journal.company_id
                JOIN res_currency currency ON currency.id = company.currency_id
               WHERE move.state not in ('draft', 'cancel')
            GROUP BY line.move_id, move.name, currency.decimal_places
              HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0
            """
        )
    else:
        cr.execute("SELECT digits FROM decimal_precision WHERE name='Account'")
        res = cr.fetchone()
        precision = min(5, res[0]) if res else 2

        cr.execute(
            """
              SELECT line.move_id,
                     CONCAT(move.name, ', with a balance of ', ROUND(SUM(line.debit - line.credit), %s))
                FROM account_move_line line
                JOIN account_move move
                  ON (line.move_id = move.id)
               WHERE move.state not in ('draft', 'cancel')
            GROUP BY line.move_id, move.name
              HAVING ROUND(SUM(line.debit - line.credit), %s) != 0.0
            """,
            [precision, precision],
        )

    count = cr.rowcount
    if count:
        extra = " (first 20 out of {})".format(count) if count > 20 else ""
        li = "".join(
            "<li>{}</li>".format(util.get_anchor_link_to_record("account.move", mid, label))
            for mid, label in cr.fetchmany(20)
        )
        msg = """
        <details>
          <summary>You have unbalanced account moves{}.</summary>
          <ul>{}</ul>
        </details>
        """.format(extra, li)

        util.add_to_migration_reports(msg, "Unbalanced Moves")
