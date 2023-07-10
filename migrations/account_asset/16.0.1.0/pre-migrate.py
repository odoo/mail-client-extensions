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
    cr.execute(
        """
        CREATE FUNCTION is_leap(y integer) RETURNS boolean
            AS 'SELECT (y % 400 = 0) OR (y % 4 = 0) AND (y % 100 != 0)'
            LANGUAGE SQL
            IMMUTABLE
            RETURNS NULL ON NULL INPUT;

        -- handles leap year date: 29th Feb, it sets 28th when non-leap
        CREATE FUNCTION make_date_leap(y integer,m integer,d integer) RETURNS date
            AS 'SELECT make_date(y,m,CASE WHEN NOT is_leap(y) AND m=2 AND d=29 THEN 28 ELSE d END)'
            LANGUAGE SQL
            IMMUTABLE
            RETURNS NULL ON NULL INPUT;
        """
    )
    fiscal_year_query = """
        UPDATE account_asset AS asset
           -- make_date_leap is a function created before on this script
           SET prorata_date =
           CASE
               WHEN method_period = '12'
               THEN make_date_leap(
                       extract(YEAR FROM asset.first_depreciation_date)::int -
                       CASE
                           WHEN make_date_leap(
                                    extract(YEAR FROM asset.first_depreciation_date)::int,
                                    company.fiscalyear_last_month::int,
                                    company.fiscalyear_last_day
                                ) < asset.first_depreciation_date
                           THEN 0 -- if fiscal last date before asset date, use same year (N)
                           ELSE 1 -- else use previous year (N - 1)
                       END,
                       company.fiscalyear_last_month::int,
                       company.fiscalyear_last_day
                    ) + INTERVAL '1 day'
                ELSE DATE(DATE_TRUNC('month', asset.first_depreciation_date))
           END
          FROM res_company AS company
         WHERE asset.company_id = company.id
           AND asset.prorata IS NOT TRUE
    """
    util.explode_execute(cr, fiscal_year_query, "account_asset", alias="asset")

    cr.execute(
        """
        DROP FUNCTION make_date_leap;
        DROP FUNCTION is_leap;
        """
    )

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
                    ) + INTERVAL '1 day', asset.prorata_date)::DATE AS computed_beginning_date
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
                   sum(line.balance) AS computed_depreciation_value
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

    query = """
        UPDATE account_asset asset
           SET account_depreciation_id = account_depreciation_expense_id,
               account_depreciation_expense_id = account_depreciation_id
         WHERE asset_type = 'sale'
    """
    util.explode_execute(cr, query, "account_asset", alias="asset")

    # As of 16.0, the imported amount is considered in the depreciation computation.
    # Until this point in the upgrade, the prorata_date has been computed to be the date at which odoo starts to
    # depreciate the asset.
    # We now want the prorata_date to be the date at which the asset was first depreciated INCLUDING the amount already
    # depreciated in a previous software (already_depreciated_amount_import).
    # In order to achieve this we shift the prorata_date by a certain number of period.
    # This shift is determined by multiplying the number of period to be depreciated in Odoo by the following ratio:
    # amount_already_depreciated_by_import / amount_to_depreciate_in_odoo
    query = """
        WITH periodic_payments AS (
            SELECT id,
                   Round((original_value - COALESCE(salvage_value, 0) - already_depreciated_amount_import)/method_number) as payment
              FROM account_asset
             WHERE {parallel_filter}
               AND method_number > 1
               AND already_depreciated_amount_import != 0
               AND (original_value - COALESCE(salvage_value, 0) - already_depreciated_amount_import) != 0
        )
        UPDATE account_asset
           SET prorata_date = prorata_date - INTERVAL '1 month' * method_period::integer * ROUND(already_depreciated_amount_import/p.payment),
               method_number = method_number + ROUND(already_depreciated_amount_import/p.payment)
          FROM periodic_payments p
         WHERE p.id = account_asset.id
           AND p.payment != 0
    """
    util.explode_execute(cr, query, "account_asset")

    # To handle assets fully depreciated in another software, as it doesnt impact any further computation,
    # we just shift the prorata_date enough to be sure it would be fully depreciated if it should be computed.
    # We don't modify the method number as we consider it correct
    query = """
        UPDATE account_asset
           SET prorata_date = prorata_date - INTERVAL '1 month' * method_period::integer * method_number
         WHERE already_depreciated_amount_import != 0
           AND (
               method_number = 1
            OR method_number > 1
           AND ROUND((original_value - COALESCE(salvage_value, 0) - already_depreciated_amount_import)/method_number) = 0
               )
    """
    util.explode_execute(cr, query, "account_asset")

    constant_period_query = """
        UPDATE account_asset
           SET prorata_computation_type = 'constant_periods'
         WHERE (prorata IS TRUE OR prorata_date != acquisition_date)
    """
    util.explode_execute(cr, constant_period_query, "account_asset")

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
