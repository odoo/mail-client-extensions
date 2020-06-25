# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense", "sample", "boolean")

    util.remove_model(cr, 'hr.expense.sheet.register.payment.wizard')
    util.create_column(cr, 'hr_expense_sheet', 'amount_residual', 'numeric')

    # Compute the residual amount on expense sheets using the same currency as the one from the company.
    cr.execute('''
        WITH amount_residual_per_sheet AS (
            SELECT
                sheet.id AS sheet_id,
                -ROUND(SUM(line.amount_residual), currency.decimal_places) AS amount_residual
            FROM hr_expense_sheet sheet
            JOIN res_company company ON company.id = sheet.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            JOIN account_move_line line ON line.move_id = sheet.account_move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
            AND line.currency_id != sheet.currency_id
            GROUP BY sheet.id, currency.decimal_places
        )
        UPDATE hr_expense_sheet
        SET amount_residual = amount_residual_per_sheet.amount_residual
        FROM amount_residual_per_sheet
        WHERE amount_residual_per_sheet.sheet_id = hr_expense_sheet.id
    ''')

    # Compute the residual amount on expense sheets using a foreign currency.
    cr.execute('''
        WITH amount_residual_per_sheet AS (
            SELECT
                sheet.id AS sheet_id,
                -ROUND(SUM(line.amount_residual_currency), currency.decimal_places) AS amount_residual
            FROM hr_expense_sheet sheet
            JOIN res_currency currency ON currency.id = sheet.currency_id
            JOIN account_move_line line ON line.move_id = sheet.account_move_id
            JOIN account_account account ON account.id = line.account_id
            WHERE account.internal_type IN ('receivable', 'payable')
            AND line.currency_id = sheet.currency_id
            GROUP BY sheet.id, currency.decimal_places
        )
        UPDATE hr_expense_sheet
        SET amount_residual = amount_residual_per_sheet.amount_residual
        FROM amount_residual_per_sheet
        WHERE amount_residual_per_sheet.sheet_id = hr_expense_sheet.id
    ''')
