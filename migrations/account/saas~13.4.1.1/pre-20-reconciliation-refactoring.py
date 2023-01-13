# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # ===========================================================
    # Reconciliation refactoring (PR:50308 & 10252)
    # ===========================================================

    # Migrate the reconciliation.

    util.create_column(cr, 'account_move', 'tax_cash_basis_move_id', 'int4')
    util.create_column(cr, 'account_partial_reconcile', 'debit_currency_id', 'int4')
    util.create_column(cr, 'account_partial_reconcile', 'credit_currency_id', 'int4')
    util.create_column(cr, 'account_partial_reconcile', 'debit_amount_currency', 'numeric')
    util.create_column(cr, 'account_partial_reconcile', 'credit_amount_currency', 'numeric')

    debit_queries = [
        '''
            UPDATE account_partial_reconcile part
            SET
                debit_currency_id = line.company_currency_id,
                debit_amount_currency = part.amount
            FROM account_move_line line
            WHERE part.currency_id IS NULL
            AND line.id = part.debit_move_id
            AND line.currency_id IS NULL
        ''',
        '''
            UPDATE account_partial_reconcile part
            SET
                debit_currency_id = line.currency_id,
                debit_amount_currency = part.amount_currency
            FROM account_move_line line
            WHERE part.currency_id IS NOT NULL
            AND line.id = part.debit_move_id
            AND line.currency_id = part.currency_id
        ''',
        '''
            UPDATE account_partial_reconcile part
            SET
                debit_currency_id = line.currency_id,
                debit_amount_currency = COALESCE(ROUND(part.amount * line.amount_currency / NULLIF(line.balance, 0.0), curr.decimal_places), 0.0)
            FROM account_move_line line
            JOIN res_currency curr ON curr.id = line.currency_id
            WHERE part.currency_id IS NULL
            AND line.id = part.debit_move_id
        ''',
    ]
    util.parallel_execute(cr, debit_queries)

    credit_queries = [
        '''
            UPDATE account_partial_reconcile part
            SET
                credit_currency_id = line.company_currency_id,
                credit_amount_currency = part.amount
            FROM account_move_line line
            WHERE part.currency_id IS NULL
            AND line.id = part.credit_move_id
            AND line.currency_id IS NULL
        ''',
        '''
            UPDATE account_partial_reconcile part
            SET
                credit_currency_id = line.currency_id,
                credit_amount_currency = part.amount_currency
            FROM account_move_line line
            WHERE part.currency_id IS NOT NULL
            AND line.id = part.credit_move_id
            AND line.currency_id = part.currency_id
        ''',
        '''
            UPDATE account_partial_reconcile part
            SET
                credit_currency_id = line.currency_id,
                credit_amount_currency = COALESCE(ROUND(part.amount * line.amount_currency / NULLIF(line.balance, 0.0), curr.decimal_places), 0.0)
            FROM account_move_line line
            JOIN res_currency curr ON curr.id = line.currency_id
            WHERE part.currency_id IS NULL
            AND line.id = part.credit_move_id
            AND line.currency_id IS NOT NULL
        ''',
    ]
    util.parallel_execute(cr, credit_queries)

    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            '''
                UPDATE account_move_line
                   SET amount_residual_currency = amount_residual
                 WHERE currency_id = company_currency_id
                   AND amount_residual_currency != amount_residual
            ''',
        ),
    )

    util.remove_field(cr, 'account.partial.reconcile', 'currency_id')
    util.remove_field(cr, 'account.partial.reconcile', 'amount_currency')

    # Migrate the cash basis base tax account.

    util.create_column(cr, 'account_chart_template', 'property_cash_basis_base_account_id', 'int4')
    util.create_column(cr, 'res_company', 'account_cash_basis_base_account_id', 'int4')
    util.create_column(cr, 'res_config_settings', 'account_cash_basis_base_account_id', 'int4')

    cr.execute('''
        WITH account_by_company AS (
            SELECT
                tax.company_id,
                ARRAY_AGG(DISTINCT tax.cash_basis_base_account_id) AS cash_basis_accounts
            FROM account_tax tax
            WHERE tax.cash_basis_base_account_id IS NOT NULL
            GROUP BY tax.company_id
        )
        UPDATE res_company
        SET account_cash_basis_base_account_id = account_by_company.cash_basis_accounts[1]
        FROM account_by_company
        WHERE account_by_company.company_id = res_company.id AND ARRAY_LENGTH(account_by_company.cash_basis_accounts, 1) = 1
    ''')

    util.remove_field(cr, 'account.tax', 'cash_basis_base_account_id')
    util.remove_field(cr, 'account.tax.template', 'cash_basis_base_account_id')
