# -*- coding: utf-8 -*-

import os

from odoo.tools import float_compare
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
    util.rename_field(cr, "account.asset", "type", "asset_type")  # was a related to category type
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
    util.remove_field(cr, "account.asset", "date_first_depreciation")
    util.remove_field(cr, "account.asset", "method_time")
    # We need to keep the purchase date to get the right currency rate in case assets are in foreign currencies
    cr.execute("ALTER TABLE account_asset ALTER COLUMN date DROP NOT NULL")

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

    if util.version_gte("saas~12.4"):
        amount_col = "amount_total"
    else:
        amount_col = "amount"

    if os.environ.get('ODOO_MIG_ACCOUNT_ASSET_MOVE_CREATION_SQL'):
        cr.execute("ALTER TABLE account_move ADD COLUMN _upg_depreciation_line_id INTEGER")
        cr.execute(
            """
                INSERT INTO account_move(
                                name, state, ref, journal_id, company_id, asset_id, _upg_depreciation_line_id,
                                date, partner_id, matched_percentage, currency_id,
                                asset_remaining_value, asset_depreciated_value,
                                %(amount_col)s
                            )
                     SELECT '/', 'draft', asset.code, category.journal_id,
                            journal.company_id, line.asset_id, line.id,
                            line.depreciation_date, partner.commercial_partner_id, 1.0, company.currency_id,
                            CASE
                                WHEN asset.currency_id = company.currency_id THEN line.remaining_value
                                ELSE ROUND(
                                     line.remaining_value::numeric * (1 / COALESCE(rate.rate, 1)),
                                     currency.decimal_places
                                     )
                            END,
                            CASE
                                WHEN asset.currency_id = company.currency_id THEN line.depreciated_value
                                ELSE ROUND(
                                     line.depreciated_value::numeric * (1 / COALESCE(rate.rate, 1)),
                                     currency.decimal_places
                                     )
                            END,
                            CASE
                                WHEN asset.currency_id = company.currency_id THEN line.amount
                                ELSE ROUND(line.amount * (1 / COALESCE(rate.rate, 1)), currency.decimal_places)
                            END
                       FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_journal journal ON journal.id = category.journal_id
                       JOIN res_company company ON company.id = journal.company_id
                  LEFT JOIN res_partner partner ON partner.id = asset.partner_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN LATERAL
                            (
                                  SELECT rate
                                    FROM res_currency_rate
                                   WHERE currency_id = currency.id AND company_id = company.id AND name <= asset.date
                                ORDER BY name DESC LIMIT 1
                            ) rate ON true
                      WHERE line.move_id IS NULL
            """ % {"amount_col": amount_col}
        )
        cr.execute(
            """
                INSERT INTO account_move_line(
                                move_id, name, company_id, account_id,
                                partner_id, analytic_account_id, date, date_maturity,
                                journal_id, user_type_id, tax_exigible,
                                company_currency_id, currency_id, amount_currency,
                                debit, credit, balance
                            )

                     SELECT move.id, asset.name, journal.company_id, category.account_depreciation_id, asset.partner_id,
                            asset.account_analytic_id, line.depreciation_date, line.depreciation_date, journal.id,
                            account.user_type_id, true, company.currency_id,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE asset.currency_id
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE -line.amount
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN GREATEST(0, -line.amount)
                                 ELSE GREATEST(0, ROUND(
                                                  -line.amount * (1 / COALESCE(rate.rate, 1)),
                                                  currency.decimal_places)
                                                  )
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN GREATEST(0, line.amount)
                                 ELSE GREATEST(0, ROUND(
                                                  line.amount * (1 / COALESCE(rate.rate, 1)),
                                                  currency.decimal_places)
                                                  )
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN -line.amount
                                 ELSE ROUND(-line.amount * (1 / COALESCE(rate.rate, 1)), currency.decimal_places)
                            END
                       FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_journal journal ON journal.id = category.journal_id
                       JOIN res_company company ON company.id = journal.company_id
                       JOIN account_move move ON move._upg_depreciation_line_id = line.id
                       JOIN account_account account ON account.id = category.account_depreciation_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN LATERAL
                            (
                                  SELECT rate
                                    FROM res_currency_rate
                                   WHERE currency_id = currency.id AND company_id = company.id AND name <= asset.date
                                ORDER BY name DESC LIMIT 1
                            ) rate ON true

                      UNION

                     SELECT move.id, asset.name, journal.company_id, category.account_depreciation_expense_id,
                            asset.partner_id, asset.account_analytic_id, line.depreciation_date, line.depreciation_date,
                            journal.id,account.user_type_id, true, company.currency_id,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE asset.currency_id
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id
                                 THEN NULL ELSE line.amount
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN GREATEST(0, line.amount)
                                 ELSE GREATEST(0, ROUND(
                                                  line.amount * (1 / COALESCE(rate.rate, 1)),
                                                  currency.decimal_places)
                                                  )
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN GREATEST(0, -line.amount)
                                 ELSE GREATEST(0, ROUND(
                                                  -line.amount * (1 / COALESCE(rate.rate, 1)),
                                                  currency.decimal_places)
                                                  )
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN line.amount
                                 ELSE ROUND(line.amount * (1 / COALESCE(rate.rate, 1)), currency.decimal_places)
                            END
                       FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_journal journal ON journal.id = category.journal_id
                       JOIN res_company company ON company.id = journal.company_id
                       JOIN account_move move ON move._upg_depreciation_line_id = line.id
                       JOIN account_account account ON account.id = category.account_depreciation_expense_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN LATERAL
                            (
                                  SELECT rate
                                    FROM res_currency_rate
                                   WHERE currency_id = currency.id AND company_id = company.id AND name <= asset.date
                                ORDER BY name DESC LIMIT 1
                            ) rate ON true
            """
        )
        cr.execute(
            """
                INSERT INTO account_analytic_tag_account_move_line_rel(
                                account_move_line_id, account_analytic_tag_id
                            )
                     SELECT move_line.id, tag.account_analytic_tag_id FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON asset.id = line.asset_id
                       JOIN account_move move ON move._upg_depreciation_line_id = line.id
                       JOIN account_move_line move_line ON move_line.move_id = move.id
                       JOIN account_analytic_tag_account_asset_asset_rel tag
                         ON tag.account_asset_asset_id = asset.id
            """
        )
        cr.execute("ALTER TABLE account_move DROP COLUMN _upg_depreciation_line_id")
    else:
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

    cr.execute(
        """
              SELECT move_id
                FROM account_asset_depreciation_line
               WHERE move_id IS NOT NULL
            GROUP BY move_id
              HAVING COUNT(*) > 1
        """
    )
    grouped_depreciation_move_ids = tuple(m[0] for m in cr.fetchall())
    if grouped_depreciation_move_ids:
        # Assets grouped by categories
        # Meaning one move can group the accounting entries of multiple assets.
        # This is no longer possible from `saas-12.3`, considering the depreciation lines are now
        # a one2many on `account.move`.
        # We therefore split such moves into pieces, so we can have one move by depreciation lines.

        # Initial checks, to make sure we don't upgrade things we do not consider (yet!)
        cr.execute(
            """
                  SELECT COUNT(*), SUM(coalesce(amount_currency, 0))
                    FROM account_move_line
                   WHERE move_id in %s
                GROUP BY move_id
            """,
            (grouped_depreciation_move_ids,),
        )
        moves = cr.fetchall()
        if any(move[0] != 2 for move in moves):
            raise NotImplementedError(
                """
                Upgrading grouped asset moves having more than one debit and one credit line
                is currently not supported.
            """
            )
        if any(move[1] != 0 for move in moves):
            raise NotImplementedError(
                """
                Upgrading grouped asset moves in foreign currencies is currently not supported.
            """
            )

        # Method used to check the global debit/credit/balance is unchanged
        def get_global_amounts():
            cr.execute(
                """
                      SELECT account_id,
                             SUM(debit) as debit,
                             SUM(credit) as credit,
                             SUM(balance) as balance
                        FROM account_move_line
                       WHERE account_id in (SELECT DISTINCT account_id FROM account_move_line WHERE move_id in %s)
                    GROUP BY account_id
                    ORDER BY account_id
                """,
                (grouped_depreciation_move_ids,),
            )
            return cr.dictfetchall()

        # Method used to check the initial moves and its splitted pieces
        # have the same debit/credit/balance by account after the split.
        def get_amounts(col):
            query = """
                  SELECT m.%(col)s as move_id, ml.account_id,
                         SUM(ml.debit) as debit,
                         SUM(ml.credit) as credit,
                         SUM(ml.balance) as balance
                    FROM account_move m
                    JOIN account_move_line ml ON ml.move_id = m.id
                   WHERE m.%(col)s in %%s
                GROUP BY m.%(col)s, ml.account_id
            """ % {
                "col": col
            }
            cr.execute(query, (tuple(grouped_depreciation_move_ids),))
            return {(r["move_id"], r["account_id"]): r for r in cr.dictfetchall()}

        # Prepare the columns we will copy from the initial move,
        # ignore the columns we assign specifically in the pieces resulting from the move split.
        m_cols = [
            list(cols)
            for cols in util.get_columns(
                cr,
                "account_move",
                ignore=("id", amount_col, "asset_id", "name", "asset_remaining_value", "asset_depreciated_value"),
                extra_prefixes=("m",),
            )
        ]
        ml_cols = [
            list(cols)
            for cols in util.get_columns(
                cr,
                "account_move_line",
                ignore=(
                    "id",
                    "move_id",
                    "debit",
                    "credit",
                    "balance",
                ),
                extra_prefixes=("ml",),
            )
        ]

        # Get the global amounts before upgrade
        global_before = get_global_amounts()

        # Add a temporary column that will be used to do the mapping move -> depreciated line.
        cr.execute(
            """
                ALTER TABLE account_move
                  ADD COLUMN _upg_depreciation_line_id INTEGER,
                  ADD COLUMN _upg_origin_move_id INTEGER,
                  ADD COLUMN _upg_depreciation_remaining BOOLEAN,
                  ADD COLUMN _upg_negative_amount BOOLEAN
            """
        )

        # Iterate on each move to split.
        # Get the rounding from the currency
        cr.execute(
            """
                SELECT m.id, c.rounding
                FROM account_move m
            LEFT JOIN res_currency c ON c.id = m.currency_id
                WHERE m.id in %s
            """,
            (grouped_depreciation_move_ids,),
        )
        roundings = dict(cr.fetchall())

        # If there are negative amounts in the depreciation lines (due to a bug), the final values of the debit/credit/balances
        # will not be consistent. This is because in the previous version the move amount is computed as the sum
        # of all depreciation amounts (e.g. if the depreciations are [1, 1, -0.5], the move amount will be 1.5), however when
        # creating a move for each depreciation line, we treat the negative amounts by inverting debit and credit, since a move
        # amount cannot be negative (so in the example above, instead of having a move line with debit 1.5 for an account, we will
        # have two move lines with debit 1 and one with credit 0.5)
        cr.execute(
            """
            SELECT id
            FROM account_asset_depreciation_line
            WHERE amount < 0
        """
        )
        has_negative_depreciation_amounts = cr.rowcount != 0

        # Get the amounts by move before upgrade
        before = get_amounts("id")

        # Create one move by depreciation line
        cr.execute(
            """
            INSERT INTO account_move(
                            _upg_origin_move_id, name, asset_id, %(amount_col)s,
                            asset_remaining_value, asset_depreciated_value, _upg_depreciation_line_id,
                            %(cols)s
                        )
                    SELECT m.id, m.name || '/' || rank() over (partition by l.move_id order by l.id),
                        l.asset_id, ABS(l.amount),
                        l.remaining_value, l.depreciated_value, l.id,
                        %(m_cols)s
                    FROM account_asset_depreciation_line l
                    JOIN account_move m ON m.id = l.move_id
                    WHERE m.id in %%s
            """
            % {"cols": ", ".join(m_cols[0]), "m_cols": ", ".join(m_cols[1]), "amount_col": amount_col},
            (grouped_depreciation_move_ids,),
        )

        # For each move created in the previous step,
        # copy the lines from the original move,
        # and assign the debit/credit/balance/move specific to the piece
        cr.execute(
            """
            INSERT INTO account_move_line(
                            move_id, debit, credit, balance,
                            %(cols)s
                        )
                    SELECT max(new_move.id),
                        CASE
                            WHEN (debit > 0 AND l.amount > 0)
                              OR (credit > 0 AND l.amount < 0) THEN ABS(l.amount)
                            ELSE 0 END,
                        CASE
                            WHEN (credit > 0 AND l.amount > 0)
                              OR (debit > 0 AND l.amount < 0) THEN ABS(l.amount)
                            ELSE 0 END,
                        CASE
                            WHEN (debit > 0 AND l.amount > 0)
                              OR (credit > 0 AND l.amount < 0) THEN ABS(l.amount)
                            ELSE -ABS(l.amount) END,
                        %(ml_cols)s
                    FROM account_asset_depreciation_line l
                    JOIN account_move m ON m.id = l.move_id
                    JOIN account_move_line ml ON ml.move_id = m.id
                    JOIN account_move new_move ON new_move._upg_depreciation_line_id = l.id
                    WHERE m.id in %%s
                GROUP BY l.id, ml.id
                RETURNING id
            """
            % {"cols": ", ".join(ml_cols[0]), "ml_cols": ", ".join(ml_cols[1])},
            (grouped_depreciation_move_ids,),
        )

        # Create a remaining move if there is a difference between the sum of the resulting pieces and the initial move
        cr.execute(
            """
            INSERT INTO account_move(_upg_origin_move_id, _upg_depreciation_remaining, name,
                                     %(amount_col)s, _upg_negative_amount, %(cols)s)
                    SELECT m.id, true, m.name || '/' || (COUNT(new_move.id) + 1)::text,
                        ABS(ROUND(m.%(amount_col)s - SUM(new_move.%(amount_col)s), currency.decimal_places)),
                        ROUND(m.%(amount_col)s - SUM(new_move.%(amount_col)s), currency.decimal_places) < 0,
                        %(m_cols)s
                    FROM account_move m
                    JOIN account_move new_move ON new_move._upg_origin_move_id = m.id
                LEFT JOIN res_currency currency ON currency.id = m.currency_id
                    WHERE m.id in %%s
                GROUP BY m.id, currency.id
                    HAVING ROUND(m.%(amount_col)s - SUM(new_move.%(amount_col)s), currency.decimal_places) != 0
            """
            % {"cols": ", ".join(m_cols[0]), "m_cols": ", ".join(m_cols[1]), "amount_col": amount_col},
            (grouped_depreciation_move_ids,),
        )
        cr.execute(
            """
            INSERT INTO account_move_line(
                            move_id, debit, credit, balance,
                            %(cols)s
                        )
                    SELECT new.id,
                        CASE
                            WHEN (ml.debit > 0 AND NOT new._upg_negative_amount)
                              OR (ml.credit > 0 AND new._upg_negative_amount) THEN new.%(amount_col)s
                            ELSE 0 END,
                        CASE
                            WHEN (ml.credit > 0 AND NOT new._upg_negative_amount)
                              OR (ml.debit > 0 AND new._upg_negative_amount) THEN new.%(amount_col)s
                            ELSE 0 END,
                        CASE
                            WHEN (ml.debit > 0 AND NOT new._upg_negative_amount)
                              OR (ml.credit > 0 AND new._upg_negative_amount) THEN new.%(amount_col)s
                            ELSE -new.%(amount_col)s END,
                        %(ml_cols)s
                    FROM account_move m
                    JOIN account_move new ON new._upg_origin_move_id = m.id AND new._upg_depreciation_remaining
                    JOIN account_move_line ml ON ml.move_id = m.id
                    WHERE m.id in %%s
            """
            % {"cols": ", ".join(ml_cols[0]), "ml_cols": ", ".join(ml_cols[1]), "amount_col": amount_col},
            (grouped_depreciation_move_ids,),
        )

        # Get the amounts by move after upgrade
        after = get_amounts("_upg_origin_move_id")

        # Check the amounts by move before upgrade are the same than after upgrade
        # If there were negative amounts in the depreciation lines, only check the balance,
        # since the total debit and credit will have changed, but the balance should still remain constant
        if has_negative_depreciation_amounts:
            for (move_id, account_id), values in before.items():
                assert (
                    float_compare(after[(move_id, account_id)]["balance"], values["balance"], precision_rounding=roundings.get(move_id, 2)) == 0
                )
        else:
            for (move_id, account_id), values in before.items():
                for k, v in values.items():
                    assert (
                        float_compare(after[(move_id, account_id)][k], v, precision_rounding=roundings.get(move_id, 2)) == 0
                    )

        # The grouped moves have been split into pieces. We can get rid of the initial moves.
        cr.execute("DELETE FROM account_move WHERE id in %s", (grouped_depreciation_move_ids,))

        # Get the global amounts after upgrade
        global_after = get_global_amounts()

        # Extra check: make sure the total debit/credit/balance globally on the accounts did not change.
        if has_negative_depreciation_amounts:
            for before, after in zip(global_before, global_after):
                assert float_compare(before["balance"], after["balance"], precision_rounding=2) == 0
        else:
            for before, after in zip(global_before, global_after):
                assert float_compare(before["debit"], after["debit"], precision_rounding=2) == 0
                assert float_compare(before["credit"], after["credit"], precision_rounding=2) == 0
                assert float_compare(before["balance"], after["balance"], precision_rounding=2) == 0

        # Cleanup the temporary columns
        cr.execute(
            """
                ALTER TABLE account_move
                 DROP COLUMN _upg_depreciation_line_id,
                 DROP COLUMN _upg_origin_move_id,
                 DROP COLUMN _upg_depreciation_remaining,
                 DROP COLUMN _upg_negative_amount
            """
        )

    cr.execute("""
           UPDATE account_move
              SET asset_id = line.asset_id,
                  asset_remaining_value = CASE
                      WHEN asset.currency_id = company.currency_id THEN line.remaining_value
                      ELSE ROUND(
                           line.remaining_value::numeric * (1 / COALESCE(rate.rate, 1)),
                           currency.decimal_places
                           )
                  END,
                  asset_depreciated_value = CASE
                      WHEN asset.currency_id = company.currency_id THEN line.depreciated_value
                      ELSE ROUND(
                           line.depreciated_value::numeric * (1 / COALESCE(rate.rate, 1)),
                           currency.decimal_places
                           )
                  END
             FROM account_asset_depreciation_line line
             JOIN account_asset asset ON asset.id = line.asset_id
             JOIN res_company company ON company.id = asset.company_id
        LEFT JOIN res_currency currency ON currency.id = asset.currency_id
        LEFT JOIN LATERAL
                  (
                        SELECT rate
                          FROM res_currency_rate
                         WHERE currency_id = currency.id AND company_id = company.id AND name <= asset.date
                      ORDER BY name DESC LIMIT 1
                  ) rate ON true
         WHERE line.move_id=account_move.id
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

    fields = "entry_count code note category_id partner_id method_end invoice_id depreciation_line_ids"
    for field in fields.split():
        util.remove_field(cr, "account.asset", field)

    util.remove_field(cr, "account.asset", "date")
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
