# -*- coding: utf-8 -*-

from odoo.addons.account_asset.models.account_asset import DAYS_PER_MONTH, DAYS_PER_YEAR

from odoo.upgrade import util
from odoo.upgrade.util.accounting import upgrade_analytic_distribution


def migrate(cr, version):

    upgrade_analytic_distribution(
        cr,
        model="account.asset",
        account_field="account_analytic_id",
    )

    # assets refactoring

    assert isinstance(DAYS_PER_MONTH, int)
    assert isinstance(DAYS_PER_YEAR, int)
    util.create_column(cr, "account_asset", "prorata_computation_type", "varchar", default="none")
    constant_period_query = """
        UPDATE account_asset
        SET prorata_computation_type = 'constant_periods'
        WHERE prorata IS TRUE
    """
    fiscal_year_query = """
        UPDATE account_asset AS asset
           SET prorata_date = CASE
               WHEN make_date(
                        extract(YEAR FROM asset.acquisition_date)::int,
                        company.fiscalyear_last_month::int,
                        company.fiscalyear_last_day
                    ) < asset.acquisition_date
               THEN make_date(
                        extract(YEAR FROM asset.acquisition_date)::int,
                        company.fiscalyear_last_month::int,
                        company.fiscalyear_last_day
                    )
               ELSE make_date(
                        extract(YEAR FROM asset.acquisition_date)::int - 1,
                        company.fiscalyear_last_month::int,
                        company.fiscalyear_last_day
                    )
               END + INTERVAL '1 day'
          FROM res_company AS company
         WHERE asset.company_id = company.id
           AND asset.prorata IS NOT TRUE
    """
    constant_period_queries = util.explode_query_range(cr, constant_period_query, "account_asset")
    fiscal_year_queries = util.explode_query_range(cr, fiscal_year_query, "account_asset", alias="asset")
    util.parallel_execute(cr, [*constant_period_queries, *fiscal_year_queries])

    util.create_column(cr, "account_move", "asset_depreciation_beginning_date", "date")
    util.create_column(cr, "account_move", "asset_number_days", "int")

    query = f"""
        WITH depreciation_moves AS (
            SELECT move.id,
                   move.date,
                   -- the following depreciation moves are supposed to cover the period right after the precedent one
                   -- as the depreciation move date is supposed to be at the end of the period, we can just add a day
                   -- to get the date of the next beginning date
                   COALESCE(LAG(move.date) OVER (
                        PARTITION BY move.asset_id
                        ORDER BY move.date
                    ) + INTERVAL '1 day', asset.prorata_date)::DATE AS computed_beginning_date,
                    asset.prorata_computation_type
              FROM account_asset AS asset
              JOIN account_move AS move ON asset.id = move.asset_id
              WHERE {{parallel_filter}}
        )
        UPDATE account_move AS am
           SET asset_depreciation_beginning_date = depreciation_moves.computed_beginning_date,
               asset_number_days = ( -- prorated days with basis of 30 days per month, see function `_get_delta_days`
                                        ( -- standardized day before end of month
                                            -- days_between(end_of_month_date - beginning_date) (included)
                                            date_part('days', (date_trunc('month', depreciation_moves.computed_beginning_date) + INTERVAL '1 month' - depreciation_moves.computed_beginning_date))
                                            -- nbr of day in this month
                                            / date_part('days', date_trunc('month', depreciation_moves.computed_beginning_date) + INTERVAL '1 month' - date_trunc('month', depreciation_moves.computed_beginning_date))
                                            * {DAYS_PER_MONTH}
                                        )
                                        + ( -- standardized day between beginning of next month and the end date in next month
                                            date_part('days', (date_trunc('month', depreciation_moves.date) + INTERVAL '1 month - 1 day' - depreciation_moves.date))
                                            -- nbr of day in this month
                                            / date_part('days', date_trunc('month', depreciation_moves.date) + INTERVAL '1 month' - date_trunc('month', depreciation_moves.date))
                                            -- standardized month
                                            * {DAYS_PER_MONTH}
                                        )
                                        -- standardized year
                                        + (date_part('year', depreciation_moves.date) - date_part('year', depreciation_moves.computed_beginning_date)) * {DAYS_PER_YEAR}
                                        -- standardized month
                                        + (date_part('month', depreciation_moves.date) - date_part('month', depreciation_moves.computed_beginning_date)) * {DAYS_PER_MONTH}
                                   )
          FROM depreciation_moves
         WHERE depreciation_moves.id = am.id
    """
    # the parallelism has to be set on account_asset because we regroup the move by asset and do a lag in order to use
    # the date of the previous move. If any move is excluded from the group by and gets in a second group by,
    # it will get the asset.prorata_date assigned which is wrong.
    util.parallel_execute(cr, util.explode_query_range(cr, query, "account_asset", alias="asset"))

    util.create_column(cr, "account_move", "depreciation_value", "numeric", default=0)
    # mimics 1st part of python method `account_move._compute_depreciation_value`
    query = """
        WITH depreciation_moves AS (
            SELECT move.id,
                   CASE
                       WHEN asset.asset_type = 'sale' THEN -sum(line.balance) ELSE sum(line.balance)
                   END AS computed_depreciation_value
              FROM account_asset AS asset
              JOIN account_move AS move ON move.asset_id = asset.id
              JOIN account_move_line AS line
                   ON line.move_id = move.id
                   AND line.account_id = asset.account_depreciation_expense_id
             WHERE {parallel_filter}
          GROUP BY asset.id, move.id
        )
        UPDATE account_move AS am
           SET depreciation_value = depreciation_moves.computed_depreciation_value
          FROM depreciation_moves
         WHERE depreciation_moves.id = am.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, "account_move", alias="move"))

    # mimics 2nd part of python method `account_move._compute_depreciation_value`
    query = """
        WITH disposal_moves AS (
           SELECT move.id AS move_id,
                  asset.original_value - asset.salvage_value - sum(
                       CASE
                           WHEN asset.original_value > 0 THEN depreciation_line.debit ELSE depreciation_line.credit
                       END
                   ) * sign(asset.original_value) AS computed_depreciation_value
             FROM account_asset AS asset
             JOIN account_move AS move ON move.asset_id = asset.id
             JOIN account_move_line AS asset_line
                -- 1) find a line emptying the asset account
                  ON asset_line.move_id = move.id
                  AND asset_line.account_id = asset.account_asset_id
                  AND asset.original_value = -asset_line.balance
             JOIN account_move_line AS depreciation_line
                -- 2) If (1) exist, find the depreciating line because it depreciates what is left in the account
                  ON depreciation_line.move_id = move.id
                  AND depreciation_line.account_id = asset.account_depreciation_id
            WHERE asset.asset_type = 'purchase'
                  AND {parallel_filter}
         GROUP BY asset.id, move.id
        )
        UPDATE account_move AS am
           SET depreciation_value = disposal_moves.computed_depreciation_value
          FROM disposal_moves
         WHERE disposal_moves.move_id = am.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, "account_move", alias="move"))

    util.remove_field(cr, "account.asset", "prorata")
    util.remove_field(cr, "account.asset", "first_depreciation_date")
    util.remove_field(cr, "account.asset", "display_model_choice")
    util.remove_field(cr, "account.asset", "depreciation_number_import")
    util.remove_field(cr, "account.asset", "first_depreciation_date_import")
    util.remove_field(cr, "account.asset", "user_type_id")

    util.remove_column(cr, "account_move", "asset_remaining_value")
    util.remove_column(cr, "account_move", "asset_depreciated_value")
    util.remove_field(cr, "account.move", "asset_manually_modified")
    util.remove_field(cr, "account.move", "asset_ids_display_name")

    util.remove_field(cr, "asset.modify", "need_date")
    util.remove_field(cr, "asset.modify", "invoice_id")
    util.remove_field(cr, "asset.modify", "invoice_line_id")

    util.remove_model(cr, "account.assets.report")

    util.remove_view(cr, "account_asset.line_caret_options")
    util.remove_view(cr, "account_asset.main_template_asset_report")
