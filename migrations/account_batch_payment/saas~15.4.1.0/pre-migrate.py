# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'account_batch_payment', 'company_currency_id', 'int4')
    query = '''
        UPDATE account_batch_payment batch
        SET company_currency_id = comp.currency_id
        FROM account_journal journal
            JOIN res_company comp ON comp.id = journal.company_id
        WHERE batch.journal_id = journal.id
    '''
    util.parallel_execute(cr, util.explode_query_range(cr, query, table='account_batch_payment', alias='batch'))

    util.create_column(cr, 'account_batch_payment', 'amount_residual', 'numeric')
    util.create_column(cr, 'account_batch_payment', 'amount_residual_currency', 'numeric')
    query = '''
        WITH outstanding_account AS (
            SELECT
                journal_id,
                ARRAY_AGG(payment_account_id) AS account_ids
            FROM account_payment_method_line
            GROUP BY journal_id
        ),
        residual_amounts AS (
            SELECT
                pay.batch_payment_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS amount_residual_currency
            FROM account_payment pay
                JOIN account_batch_payment batch ON batch.id = pay.batch_payment_id
                LEFT JOIN account_payment_method_line pay_method ON pay_method.id = pay.payment_method_line_id
                JOIN account_move move ON move.id = pay.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                LEFT JOIN outstanding_account ON outstanding_account.journal_id = journal.id
                JOIN res_company comp ON comp.id = journal.company_id
                JOIN account_move_line line ON line.payment_id = pay.id
            WHERE line.account_id IS NOT NULL
                AND line.account_id = ANY(
                    outstanding_account.account_ids
                    || journal.default_account_id
                    || pay_method.payment_account_id
                    || comp.account_journal_payment_debit_account_id
                    || comp.account_journal_payment_credit_account_id
                )
                AND {parallel_filter}
            GROUP BY pay.batch_payment_id
        )
        UPDATE account_batch_payment
        SET
            amount_residual = COALESCE(residual_amounts.amount_residual, 0.0),
            amount_residual_currency = COALESCE(residual_amounts.amount_residual_currency, 0.0)
        FROM residual_amounts
        WHERE residual_amounts.batch_payment_id = account_batch_payment.id
    '''
    util.parallel_execute(cr, util.explode_query_range(cr, query, table='account_batch_payment', alias='batch'))
