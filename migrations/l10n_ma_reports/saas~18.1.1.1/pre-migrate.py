from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_ma_reports_payment_method", "varchar")
    util.explode_execute(
        cr,
        """
        WITH payments_per_move AS (
            SELECT move.id AS move_id,
                   (ARRAY_AGG(payment.l10n_ma_reports_payment_method ORDER BY payment.date DESC))[1] AS l10n_ma_reports_payment_method
              FROM account_move move
              JOIN account_move_line aml
                ON aml.move_id = move.id
              JOIN account_account account
                ON aml.account_id = account.id
              JOIN account_partial_reconcile partial
                ON partial.credit_move_id = aml.id
                OR partial.debit_move_id = aml.id
              JOIN account_move_line rec_aml
                ON partial.debit_move_id = rec_aml.id
                OR partial.credit_move_id = rec_aml.id
              JOIN account_move rec_move
                ON rec_aml.move_id = rec_move.id
              JOIN account_payment payment
                ON payment.id = rec_move.origin_payment_id
             WHERE account.account_type IN ('asset_receivable', 'liability_payable')
               AND {parallel_filter}
             GROUP BY move.id
        )
        UPDATE account_move move
           SET l10n_ma_reports_payment_method = ppm.l10n_ma_reports_payment_method
          FROM payments_per_move ppm
         WHERE move.id = ppm.move_id
        """,
        table="account_move",
        alias="move",
    )
