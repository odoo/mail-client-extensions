from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        WITH lines AS (
            UPDATE account_bank_statement_line
               SET amount_currency = -amount_currency
             WHERE amount_currency != 0
               AND SIGN(amount) != SIGN(amount_currency)
         RETURNING statement_id
        )
        SELECT s.id, s.name
          FROM account_bank_statement s
          JOIN lines l
            ON l.statement_id = s.id
      GROUP BY s.id, s.name
        """
    )

    if cr.rowcount:
        util.add_to_migration_reports(
            category="Accounting",
            message=(
                """
                <details>
                    <summary>
                        In your database we found bank statements with lines having a different sign (+/-)
                        for the values of the fields 'amount' and 'amount_currency'.
                        This inconsistency was blocking the upgrade process.
                        Assuming `amount` to be correct, the sign of `amount_currency` was automatically switched.
                        Please, check the involved bank statements below.
                        If the automatic fix was incorrect, update the value of `amount` and/or `amount_currency`
                        accordingly and submit a new upgrade request.
                    </summary>
                    <ul>%s</ul>
                </details>
                """
                % " ".join(
                    [
                        f"<li>{util.get_anchor_link_to_record('account.bank.statement', id, name)}</li>"
                        for id, name in cr.fetchall()
                    ]
                )
            ),
            format="html",
        )
