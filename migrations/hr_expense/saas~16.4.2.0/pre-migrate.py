from odoo.upgrade import util


def migrate(cr, version):
    # Reverse the relation of hr.expense.sheet.account_move_id and account.move.expense_sheet_id
    # to allow multiple moves linked to one expense.sheet

    util.create_column(cr, "account_move", "expense_sheet_id", "int4")
    util.explode_execute(
        cr,
        """
        WITH am_hes AS (
            SELECT hes.account_move_id AS move_id,
                   min(hes.id) AS sheet_id
              FROM hr_expense_sheet AS hes
              JOIN account_move am -- for // filter
                ON hes.account_move_id = am.id
             WHERE {parallel_filter}
             GROUP BY hes.account_move_id
            )
        UPDATE account_move am
           SET expense_sheet_id = am_hes.sheet_id
          FROM am_hes
         WHERE am.id = am_hes.move_id
        """,
        table="account_move",
        alias="am",
    )
    util.remove_field(cr, "hr.expense.sheet", "account_move_id")
