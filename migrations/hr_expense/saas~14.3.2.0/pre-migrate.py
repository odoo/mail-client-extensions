# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense_sheet", "approval_date", "timestamp without time zone")
    cr.execute(
        """
            UPDATE hr_expense_sheet
               SET approval_date = write_date
             WHERE state IN ('approve', 'post', 'done')
        """
    )

    # Add and set new hr_expense_sheet field: payment_state.
    # Updating account_move_id payment_state therfore needed.
    in_payment_state = "in_payment" if util.module_installed(cr, "account_accountant") else "paid"
    cr.execute(
        """
        WITH part_rec_select AS (
                SELECT sheet.account_move_id move_id,
                       BOOL_AND(COALESCE(payment.is_matched, false)) all_is_matched
                  FROM account_partial_reconcile AS part_rec
                  JOIN account_move_line credit_aml ON part_rec.credit_move_id = credit_aml.id
                  JOIN account_move_line debit_aml ON part_rec.debit_move_id = debit_aml.id
                  JOIN hr_expense_sheet sheet ON sheet.account_move_id = credit_aml.move_id
             LEFT JOIN account_payment payment ON payment.move_id = debit_aml.move_id
              GROUP BY sheet.account_move_id
            ),
            move_select AS (
                SELECT sheet.account_move_id AS move_id,
                       CASE WHEN sheet.state = 'done' AND part_rec_select.all_is_matched THEN 'paid'
                            WHEN sheet.state = 'done' THEN %s
                            WHEN part_rec_select.move_id = sheet.account_move_id THEN 'partial'
                            ELSE 'not_paid' END AS payment_state
                  FROM hr_expense_sheet sheet
             LEFT JOIN part_rec_select ON part_rec_select.move_id = sheet.account_move_id
                 WHERE sheet.account_move_id IS NOT NULL
            )
        UPDATE account_move
           SET payment_state = move_select.payment_state
          FROM move_select
         WHERE account_move.id = move_select.move_id
        """,
        [in_payment_state],
    )
    util.create_column(cr, "hr_expense_sheet", "payment_state", "varchar", default="not_paid")
    cr.execute(
        """
        UPDATE hr_expense_sheet sheet
           SET payment_state = move.payment_state
          FROM account_move move
         WHERE move.id = sheet.account_move_id
        """
    )
