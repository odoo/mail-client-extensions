# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def _convert_to_account_move_vals(depr_line):
    return {
        'ref': depr_line['asset_code'],
        'date': depr_line['depreciation_date'],
        'journal_id': depr_line['journal_id'],
        'line_ids': [
            (0, 0, {
                'name': depr_line['asset_name'],
                'account_id': depr_line['account_depreciation_id'],
                'debit': max(0, -depr_line['amount']),
                'credit': max(0, depr_line['amount']),
                'partner_id': depr_line['partner_id'],
                'analytic_tag_ids': [(6, 0, depr_line['analytic_tag_ids'])],
                'analytic_account_id': depr_line['account_analytic_id'],
            }),
            (0, 0, {
                'name': depr_line['asset_name'],
                'account_id': depr_line['account_depreciation_expense_id'],
                'debit': max(0, depr_line['amount']),
                'credit': max(0, -depr_line['amount']),
                'partner_id': depr_line['partner_id'],
                'analytic_tag_ids': [(6, 0, depr_line['analytic_tag_ids'])],
                'analytic_account_id': depr_line['account_analytic_id'],
            }),
        ]
    }


def migrate(cr, version):
    util.create_column(cr, 'account_account', 'asset_model', 'int4')
    util.create_column(cr, 'account_account', 'create_asset', 'varchar')

    cr.execute("UPDATE account_account SET create_asset='no'")

    util.rename_model(cr, 'account.asset.asset', 'account.asset')

    util.create_column(cr, 'account_asset', 'value_residual', 'numeric')
    util.create_column(cr, 'account_asset', 'prorata_date', 'date')
    util.create_column(cr, 'account_asset', 'asset_type', 'varchar')
    util.rename_field(cr, "account.asset", "first_depreciation_manual_date", "first_depreciation_date")
    util.create_column(cr, 'account_asset', 'disposal_date', 'date')
    util.create_column(cr, 'account_asset', 'account_asset_id', 'int4')
    util.create_column(cr, 'account_asset', 'account_depreciation_id', 'int4')
    util.create_column(cr, 'account_asset', 'account_depreciation_expense_id', 'int4')
    util.create_column(cr, 'account_asset', 'journal_id', 'int4')
    util.create_column(cr, 'account_asset', 'model_id', 'int4')

    cr.execute("UPDATE account_asset SET first_depreciation_date = date WHERE first_depreciation_date IS NULL")
    cr.execute("UPDATE account_asset SET prorata_date = first_depreciation_date WHERE prorata_date IS NULL")

    # these columns are "not null". Remove them now to avoid having to specify them in the next query
    util.remove_field(cr, "account.asset", "date")
    util.remove_field(cr, "account.asset", "date_first_depreciation")
    util.remove_field(cr, "account.asset", "method_time")

    cr.execute("""
        INSERT INTO account_asset
            (state,category_id,active, name, account_analytic_id,
            account_asset_id,account_depreciation_id,
            account_depreciation_expense_id,journal_id,company_id,method,
            method_number,method_period,method_progress_factor,
            prorata,currency_id,first_depreciation_date,value)
             SELECT 'model' as state,ac.id,
                    ac.active,ac.name,ac.account_analytic_id,ac.account_asset_id,
                    ac.account_depreciation_id,ac.account_depreciation_expense_id,
                    ac.journal_id,ac.company_id,ac.method,ac.method_number,
                    ac.method_period,ac.method_progress_factor,
                    ac.prorata,c.currency_id,CURRENT_DATE,0
               FROM account_asset_category ac
               INNER JOIN res_company c on ac.company_id=c.id
    """)

    cr.execute("""
        UPDATE account_asset
           SET asset_type=c.type,
               account_asset_id=c.account_asset_id,
               account_depreciation_id=c.account_depreciation_id,
               account_depreciation_expense_id=c.account_depreciation_expense_id,
               journal_id=c.journal_id
          FROM account_asset_category c
         WHERE account_asset.category_id=c.id
    """)
    cr.execute("""
        ALTER TABLE account_asset
        ALTER COLUMN method_period TYPE varchar
        USING CASE WHEN method_period = '1' THEN '1' ELSE '12' END
    """)

    util.create_column(cr, 'account_move', 'asset_id', 'int4')
    util.create_column(cr, 'account_move', 'asset_remaining_value', 'numeric')
    util.create_column(cr, 'account_move', 'asset_depreciated_value', 'numeric')
    util.create_column(cr, 'account_move', 'asset_manually_modified', 'boolean')
    cr.execute("""
        SELECT
            asset.code AS asset_code,
            line.depreciation_date,
            category.journal_id,
            asset.id AS asset_id,
            line.remaining_value,
            line.depreciated_value,
            asset.name AS asset_name,
            category.account_depreciation_id,
            category.account_depreciation_expense_id,
            line.amount,
            asset.partner_id,
            asset.account_analytic_id,
            array_remove(ARRAY_AGG(tags.account_analytic_tag_id), NULL) AS analytic_tag_ids
        FROM account_asset_depreciation_line line
        JOIN account_asset asset ON line.asset_id = asset.id
        JOIN account_asset_category category ON asset.category_id = category.id
        LEFT JOIN account_analytic_tag_account_asset_asset_rel tags ON account_asset_asset_id = asset.id
        WHERE line.move_id IS NULL
        GROUP BY
            asset.code,
            line.depreciation_date,
            category.journal_id,
            asset.id,
            line.remaining_value,
            line.depreciated_value,
            asset.name,
            category.account_depreciation_id,
            category.account_depreciation_expense_id,
            line.amount,
            asset.partner_id,
            asset.account_analytic_id
    """)
    env = util.env(cr)
    result = cr.dictfetchall()
    move_ids = env["account.move"].create([_convert_to_account_move_vals(res) for res in result])
    cr.executemany("""
        UPDATE account_move SET
            asset_id=%s,
            asset_remaining_value=%s,
            asset_depreciated_value=%s
        WHERE id=%s
    """, list(zip(
        [res['asset_id'] for res in result],
        [res['remaining_value'] for res in result],
        [res['depreciated_value'] for res in result],
        move_ids.ids
    )))

    cr.execute("""
        UPDATE account_move
           SET asset_id=d.asset_id,
               asset_remaining_value=d.remaining_value,
               asset_depreciated_value=d.depreciated_value
          FROM account_asset_depreciation_line d
         WHERE d.move_id=account_move.id
    """)
    cr.execute("""
        UPDATE account_move
           SET auto_post=TRUE
         WHERE state!='posted'
           AND asset_id IS NOT NULL
    """)
    util.create_column(cr, 'account_move_line', 'asset_id', 'int4')

    util.create_column(cr, 'asset_modify', 'asset_id', 'int4')
    util.remove_field(cr, 'asset.modify', 'method_period')
    util.create_column(cr, 'asset_modify', 'method_period', 'varchar')
    util.create_column(cr, 'asset_modify', 'value_residual', 'numeric')
    util.create_column(cr, 'asset_modify', 'salvage_value', 'numeric')
    util.create_column(cr, 'asset_modify', 'currency_id', 'int4')
    util.create_column(cr, 'asset_modify', 'resume_date', 'date')
    util.create_column(cr, 'asset_modify', 'need_date', 'boolean')

    util.remove_field(cr, 'account.asset', 'code')
    util.remove_field(cr, 'account.asset', 'partner_id')
    util.remove_field(cr, 'account.asset', 'method_end')
    util.remove_field(cr, 'account.asset', 'invoice_id')

    util.remove_field(cr, 'account.move', 'asset_depreciation_ids')
    util.remove_field(cr, 'account.invoice.line', 'asset_category_id')
    util.remove_field(cr, 'account.invoice.line', 'asset_mrr')
    util.remove_field(cr, 'asset.modify', 'method_end')
    util.remove_field(cr, 'asset.modify', 'asset_method_time')

    util.remove_field(cr, 'product.template', 'asset_category_id')
    util.remove_field(cr, 'product.template', 'deferred_revenue_category_id')

    util.remove_model(cr, 'account.asset.category')
    util.remove_model(cr, 'account.asset.depreciation.line')
    util.remove_model(cr, 'asset.asset.report')
    util.remove_model(cr, 'asset.depreciation.confirmation.wizard')
