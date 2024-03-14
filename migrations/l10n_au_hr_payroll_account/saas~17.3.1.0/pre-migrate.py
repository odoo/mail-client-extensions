from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE l10n_au_super_account SET date_from = create_date WHERE date_from IS NULL")

    util.remove_column(cr, "l10n_au_super_stream_line", "payee_id")
    util.remove_column(cr, "l10n_au_super_stream_line", "currency_id")

    cr.execute(
        """
        WITH accounts AS (
          SELECT min(id) as id, employee_id
            FROM l10n_au_super_account
          GROUP BY employee_id
        )
        UPDATE l10n_au_super_stream_line l
           SET super_account_id = a.id
          FROM accounts a
         WHERE l.employee_id = a.employee_id
           AND l.super_account_id IS NULL
        """
    )
