# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_account', 'asset_model', 'int4')
    util.create_column(cr, 'account_account', 'create_asset', 'varchar')

    cr.execute("UPDATE account_account SET create_asset='no'")

    util.rename_model(cr, 'account.asset.asset', 'account.asset')

    util.rename_field(cr, 'account.asset', 'method_period', 'method_period_old')
    util.create_column(cr, 'account_asset', 'method_period', 'varchar')
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
            prorata,currency_id,method_period_old,first_depreciation_date,value)
             SELECT 'model' as state,ac.id,
                    ac.active,ac.name,ac.account_analytic_id,ac.account_asset_id,
                    ac.account_depreciation_id,ac.account_depreciation_expense_id,
                    ac.journal_id,ac.company_id,ac.method,ac.method_number,
                    ac.method_period,ac.method_progress_factor,
                    ac.prorata,c.currency_id,ac.method_period,CURRENT_DATE,0
               FROM account_asset_category ac
               INNER JOIN res_company c on ac.company_id=c.id
    """)

    cr.execute("""
        UPDATE account_asset
           SET asset_type=c.type,
               account_asset_id=c.account_asset_id,
               account_depreciation_id=c.account_depreciation_id,
               account_depreciation_expense_id=c.account_depreciation_expense_id,
               journal_id=c.journal_id,
               method_period=CASE WHEN method_period_old=1 THEN '1' ELSE '12' END
          FROM account_asset_category c
         WHERE account_asset.category_id=c.id
    """)

    util.create_column(cr, 'account_move', 'asset_id', 'int4')
    util.create_column(cr, 'account_move', 'asset_remaining_value', 'numeric')
    util.create_column(cr, 'account_move', 'asset_depreciated_value', 'numeric')
    util.create_column(cr, 'account_move', 'asset_manually_modified', 'boolean')
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

    util.remove_field(cr, 'account.asset', 'method_period_old')
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
