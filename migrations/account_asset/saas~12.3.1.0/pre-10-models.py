from collections import defaultdict

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.accounting import no_deprecated_accounts


def migrate(cr, version):
    with no_deprecated_accounts(cr):
        _migrate(cr, version)


def _migrate(cr, version):
    env = util.env(cr)
    rate_subquery = """
                      (
                            SELECT rate
                              FROM res_currency_rate
                             WHERE currency_id = currency.id AND company_id = company.id AND name <= asset.date
                          ORDER BY name DESC LIMIT 1
                      )"""

    util.create_column(cr, "account_account", "asset_model", "int4")
    util.create_column(cr, "account_account", "create_asset", "varchar")

    cr.execute("UPDATE account_account SET create_asset='no'")

    util.rename_model(cr, "account.asset.asset", "account.asset", ignored_m2ms=())

    util.create_column(cr, "account_asset", "value_residual", "numeric")
    util.create_column(cr, "account_asset", "prorata_date", "date")
    util.rename_field(cr, "account.asset", "type", "asset_type")  # was a related to category type
    util.create_column(cr, "account_asset", "asset_type", "varchar")
    util.rename_field(cr, "account.asset", "first_depreciation_manual_date", "first_depreciation_date")
    util.create_column(cr, "account_asset", "disposal_date", "date")
    util.create_column(cr, "account_asset", "account_asset_id", "int4")
    util.create_column(cr, "account_asset", "account_depreciation_id", "int4")
    util.create_column(cr, "account_asset", "account_depreciation_expense_id", "int4")
    util.create_column(cr, "account_asset", "journal_id", "int4")
    util.create_column(cr, "account_asset", "model_id", "int4")

    cr.execute("UPDATE account_asset SET first_depreciation_date = date WHERE first_depreciation_date IS NULL")
    cr.execute("UPDATE account_asset SET prorata_date = first_depreciation_date WHERE prorata_date IS NULL")

    # these columns are "not null". Remove them now to avoid having to specify them in the next query
    util.remove_field(cr, "account.asset", "date_first_depreciation")
    util.remove_field(cr, "account.asset", "method_time")
    # We need to keep the purchase date to get the right currency rate in case assets are in foreign currencies
    cr.execute("ALTER TABLE account_asset ALTER COLUMN date DROP NOT NULL")

    cr.execute(
        """
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
    """
    )

    cr.execute(
        """
        UPDATE account_asset
           SET asset_type = c.type,
               account_asset_id = c.account_asset_id,
               account_depreciation_id = c.account_depreciation_id,
               account_depreciation_expense_id = c.account_depreciation_expense_id,
               journal_id = c.journal_id
          FROM account_asset_category c
         WHERE account_asset.category_id = c.id
    """
    )

    cr.execute(
        """
        UPDATE account_asset a
           SET model_id = a2.id
          FROM account_asset a2
         WHERE a2.category_id = a.category_id
           AND a2.state = 'model'
           AND a.state <> 'model'
    """
    )

    cr.execute(
        """
        ALTER TABLE account_asset
        ALTER COLUMN method_period TYPE varchar
        USING CASE WHEN method_period = '1' THEN '1' ELSE '12' END
    """
    )

    util.create_column(cr, "account_move", "asset_id", "int4")
    util.create_column(cr, "account_move", "asset_remaining_value", "numeric")
    util.create_column(cr, "account_move", "asset_depreciated_value", "numeric")
    util.create_column(cr, "account_move", "asset_manually_modified", "boolean")

    if util.version_gte("saas~12.4"):
        amount_col = "amount_total"
    else:
        amount_col = "amount"

    cr.execute("SELECT DISTINCT company_id FROM account_asset")
    migration_journals = env["account.journal"].create(
        [
            {
                "name": "Assets Upgrade",
                "code": "UPGASSET",
                "type": "general",
                "company_id": cid[0],
                "active": False,
            }
            for cid in cr.fetchall() or [[env.user.company_id.id]]
        ]
    )

    cr.execute("ALTER TABLE account_move ADD COLUMN _upg_depreciation_line_id INTEGER")
    cr.execute(
        f"""
                INSERT INTO account_move(
                                name, state, ref, journal_id, company_id, asset_id, _upg_depreciation_line_id,
                                date, partner_id, currency_id,
                                asset_remaining_value, asset_depreciated_value,
                                {amount_col}
                            )
                /* Add the lines that don't have a depreciation created yet in the journal set on the category */
                     SELECT '/', 'draft', COALESCE(asset.code, asset.name), category.journal_id,
                            journal.company_id, line.asset_id, line.id,
                            line.depreciation_date, partner.commercial_partner_id, company.currency_id,
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
                  LEFT JOIN LATERAL {rate_subquery} rate ON true
                      WHERE line.move_id IS NULL

                      UNION ALL

                /* Add the lines that already have a depreciation created in a new journal created
                   for the migration if the move has been modified or grouped */
                     SELECT '/', 'draft', COALESCE(asset.code, asset.name), journal.id,
                            journal.company_id, line.asset_id, line.id,
                            line.depreciation_date, partner.commercial_partner_id, company.currency_id,
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
                       JOIN account_move move ON line.move_id = move.id
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_journal journal ON journal.company_id = asset.company_id
                                                   AND journal.id IN %(journal_ids)s
                       JOIN res_company company ON company.id = asset.company_id
                  LEFT JOIN res_partner partner ON partner.id = asset.partner_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN LATERAL {rate_subquery} rate ON true
                      WHERE move.amount - line.amount > 0.001
                         OR move.id IN (
                             SELECT move.id
                               FROM account_move move
                               JOIN account_move_line aml ON move.id = aml.move_id
                               JOIN account_asset_depreciation_line adl ON move.id = adl.move_id
                           GROUP BY move.id
                             HAVING COUNT(*) != 2
                         )
    """,
        {
            "journal_ids": tuple(migration_journals.ids),
        },
    )
    cr.execute(
        f"""
                INSERT INTO account_move_line(
                                move_id, name, company_id, account_id, ref,
                                partner_id, analytic_account_id, date, date_maturity,
                                journal_id, user_type_id, tax_exigible,
                                company_currency_id, currency_id, amount_currency,
                                debit, credit, balance
                            )

                     SELECT move.id, asset.name, journal.company_id, category.account_depreciation_id, move.ref, asset.partner_id,
                            asset.account_analytic_id, line.depreciation_date, line.depreciation_date, journal.id,
                            account.user_type_id, true, company.currency_id,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE asset.currency_id
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE ROUND(-line.amount, currency.decimal_places)
                            END,
                            GREATEST(0, ROUND(
                                CASE
                                    WHEN asset.currency_id = company.currency_id THEN -line.amount
                                    ELSE -line.amount * (1 / COALESCE(rate.rate, 1))
                                END, company_currency.decimal_places
                            )),
                            GREATEST(0, ROUND(
                                CASE
                                    WHEN asset.currency_id = company.currency_id THEN line.amount
                                    ELSE line.amount * (1 / COALESCE(rate.rate, 1))
                                END, company_currency.decimal_places
                            )),
                            ROUND(
                                CASE
                                    WHEN asset.currency_id = company.currency_id THEN -line.amount
                                    ELSE -line.amount * (1 / COALESCE(rate.rate, 1))
                                END, company_currency.decimal_places
                            )
                       FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_move move ON move._upg_depreciation_line_id = line.id
                       JOIN account_journal journal ON journal.id = move.journal_id
                       JOIN res_company company ON company.id = journal.company_id
                       JOIN account_account account ON account.id = category.account_depreciation_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN res_currency company_currency ON company_currency.id = company.currency_id
                  LEFT JOIN LATERAL {rate_subquery} rate ON true

                      UNION ALL

                     SELECT move.id, asset.name, journal.company_id, category.account_depreciation_expense_id, move.ref,
                            asset.partner_id, asset.account_analytic_id, line.depreciation_date, line.depreciation_date,
                            journal.id,account.user_type_id, true, company.currency_id,
                            CASE
                                 WHEN asset.currency_id = company.currency_id THEN NULL
                                 ELSE asset.currency_id
                            END,
                            CASE
                                 WHEN asset.currency_id = company.currency_id
                                 THEN NULL ELSE ROUND(line.amount, currency.decimal_places)
                            END,
                            GREATEST(0, ROUND(
                                CASE
                                    WHEN asset.currency_id = company.currency_id THEN line.amount
                                    ELSE line.amount * (1 / COALESCE(rate.rate, 1))
                                END, company_currency.decimal_places
                            )),
                            GREATEST(0, ROUND(
                                CASE
                                    WHEN asset.currency_id = company.currency_id THEN -line.amount
                                    ELSE -line.amount * (1 / COALESCE(rate.rate, 1))
                                END, company_currency.decimal_places
                            )),
                            ROUND(
                                 CASE
                                     WHEN asset.currency_id = company.currency_id THEN line.amount
                                     ELSE line.amount * (1 / COALESCE(rate.rate, 1))
                                 END, company_currency.decimal_places
                            )
                       FROM account_asset_depreciation_line line
                       JOIN account_asset asset ON line.asset_id = asset.id
                       JOIN account_asset_category category ON asset.category_id = category.id
                       JOIN account_move move ON move._upg_depreciation_line_id = line.id
                       JOIN account_journal journal ON journal.id = move.journal_id
                       JOIN res_company company ON company.id = journal.company_id
                       JOIN account_account account ON account.id = category.account_depreciation_expense_id
                  LEFT JOIN res_currency currency ON currency.id = asset.currency_id
                  LEFT JOIN res_currency company_currency ON company_currency.id = company.currency_id
                  LEFT JOIN LATERAL {rate_subquery} rate ON true
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
                       JOIN account_analytic_tag_account_asset_rel tag
                         ON tag.account_asset_id = asset.id
    """
    )

    # Reverse the moves linked to depreciation lines so that the migration journals are balanced
    cr.execute("ALTER TABLE account_move ADD COLUMN _upg_original_move INTEGER")
    cr.execute(
        f"""
        INSERT INTO account_move (
                        name, state, ref, journal_id, company_id, _upg_original_move,
                        date, partner_id, currency_id, {amount_col}
                    )
             SELECT '/', 'draft', original.name, journal.id, journal.company_id, original.id,
                    original.date, original.partner_id, original.currency_id, original.{amount_col}
               FROM account_move original
               JOIN account_journal journal ON journal.company_id = original.company_id
                                           AND journal.id in %(journal_ids)s
              WHERE original.id IN (
                SELECT DISTINCT move_id
                  FROM account_asset_depreciation_line line
                  JOIN account_move move ON line.id = move._upg_depreciation_line_id
              )
    """,
        {
            "journal_ids": tuple(migration_journals.ids),
        },
    )
    cr.execute(
        """
        INSERT INTO account_move_line(
                        move_id, name, company_id, account_id,
                        partner_id, analytic_account_id, date, date_maturity,
                        journal_id, user_type_id, tax_exigible,
                        company_currency_id, currency_id, amount_currency,
                        debit,
                        credit,
                        balance
                    )
             SELECT new.id, original.name, original.company_id, original.account_id,
                    original.partner_id, original.analytic_account_id, original.date, original.date_maturity,
                    new.journal_id, original.user_type_id, original.tax_exigible,
                    original.company_currency_id, original.currency_id, -original.amount_currency,
                    ROUND(original.credit, company_currency.decimal_places),
                    ROUND(original.debit, company_currency.decimal_places),
                    ROUND(-original.balance, company_currency.decimal_places)
               FROM account_move original_move
               JOIN account_move new ON original_move.id = new._upg_original_move
               JOIN account_move_line original ON original.move_id = original_move.id
               JOIN res_currency company_currency ON company_currency.id = original.company_currency_id
    """
    )

    cr.execute(
        """
        UPDATE account_asset_depreciation_line line
           SET move_id = move.id
          FROM account_move move
         WHERE move._upg_depreciation_line_id = line.id
    """
    )
    cr.execute(
        """
        UPDATE account_move original
           SET reverse_entry_id = new.id
          FROM account_move new
         WHERE new._upg_original_move = original.id
    """
    )
    cr.execute("ALTER TABLE account_move DROP COLUMN _upg_original_move")
    cr.execute("ALTER TABLE account_move DROP COLUMN _upg_depreciation_line_id")

    # Balance the journal so that it has a zero balance for each account at any point of time.
    cr.execute(
        """
          SELECT journal_id, date, account_id, SUM(balance)
            FROM account_move_line
           WHERE journal_id IN %(journal_ids)s
        GROUP BY account_id, journal_id, date
    """,
        {
            "journal_ids": tuple(migration_journals.ids),
        },
    )

    unbalanced_by_journal = defaultdict(list)
    for unbalanced in cr.fetchall():
        unbalanced_by_journal[(unbalanced[0], unbalanced[1])].append((unbalanced[2], unbalanced[3]))

    # Ignore roundings, in case the rounding of the currency has been changed after the asset move lines were created
    origin_rounding = {}
    for currency in migration_journals.mapped("company_id.currency_id"):
        origin_rounding[currency] = (currency.rounding, currency.decimal_places)
        currency.rounding = 1e-6

    balance_moves = env["account.move"].create(
        [
            {
                "journal_id": journal_id,
                "date": date,
                "ref": "Upgrade balance",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": account_id,
                            "debit": max(0, -balance),
                            "credit": max(0, balance),
                        },
                    )
                    for account_id, balance in values
                ],
            }
            for (journal_id, date), values in unbalanced_by_journal.items()
        ]
    )

    for currency, (rounding, decimal_places) in origin_rounding.items():
        cr.execute(
            """
                UPDATE res_currency SET rounding = %s, decimal_places = %s WHERE id = %s
            """,
            [rounding, decimal_places, currency.id],
        )
        currency.invalidate_cache(["rounding"], currency.ids)

    # Post the created moves
    cr.execute("SELECT DISTINCT date_part('year', date)::int FROM account_move")
    years = [d[0] for d in cr.fetchall()]

    for journal in migration_journals:
        for year in years:
            cr.execute("CREATE TEMP SEQUENCE temp_sequence_%s_%s", [year, journal.id])
    cr.execute(
        """
        -- Use a CTE to control the order of updates
        WITH cte AS (
            SELECT move.id,
                   CONCAT(
                       'UPGASSET/', date_part('year', move.date)::int, '/',
                       lpad(nextval('temp_sequence_' || date_part('year', move.date) || '_' || journal.id)::int::text, 8, '0')
                   ) AS name
              FROM account_move move
              JOIN account_journal journal ON move.journal_id = journal.id
             WHERE journal.id IN %(journal_ids)s
          ORDER BY move.date, move.id
        )

        UPDATE account_move m SET state='posted', name = cte.name
          FROM cte
         WHERE m.id = cte.id
    """,
        {
            "journal_ids": tuple(migration_journals.ids),
        },
    )

    # Remove useless journals when it was not needed
    cr.execute(
        """
        SELECT journal.id
          FROM account_journal journal
         WHERE id IN %(journal_ids)s
           AND NOT EXISTS (SELECT 1 FROM account_move WHERE journal_id = journal.id)
    """,
        {
            "journal_ids": tuple(migration_journals.ids),
        },
    )
    env["account.journal"].browse(j[0] for j in cr.fetchall()).unlink()

    if balance_moves:
        balance_moves.invalidate_cache()
        lis = "\n".join(
            "<li>account.move record #%s: %s, account.journal record: #%s</li>"
            % (m.id, util.html_escape(m.name), m.journal_id.id)
            for m in balance_moves
        )
        util.add_to_migration_reports(
            message=f"""
                <details>
                  <summary>
                    Some inconsistencies have been found between Asset/Deferred Revenue Depreciation
                    Lines and the related Journal Entries. This can happen if you edited manually the
                    Journal Entries <br>A journal has been created with the corresponding balancing
                    Journal Entries.
                  </summary>
                  <ul>
                    {lis}
                  </ul>
                </details>
            """,
            format="html",
            category="Accounting",
        )

    cr.execute(
        f"""
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
        LEFT JOIN LATERAL {rate_subquery} rate ON true
         WHERE line.move_id=account_move.id
    """
    )
    cr.execute(
        """
        UPDATE account_move move
           SET auto_post = TRUE
          FROM account_asset asset
         WHERE move.state != 'posted'
           AND move.asset_id = asset.id
           AND asset.active
    """
    )
    util.create_column(cr, "account_move_line", "asset_id", "int4")

    util.create_column(cr, "asset_modify", "asset_id", "int4")
    util.remove_field(cr, "asset.modify", "method_period")
    util.create_column(cr, "asset_modify", "method_period", "varchar")
    util.create_column(cr, "asset_modify", "value_residual", "numeric")
    util.create_column(cr, "asset_modify", "salvage_value", "numeric")
    util.create_column(cr, "asset_modify", "currency_id", "int4")
    util.create_column(cr, "asset_modify", "resume_date", "date")
    util.create_column(cr, "asset_modify", "need_date", "boolean")

    fields = "entry_count code note category_id partner_id method_end invoice_id depreciation_line_ids"
    for field in fields.split():
        util.remove_field(cr, "account.asset", field)

    util.remove_field(cr, "account.asset", "date")
    util.remove_field(cr, "account.move", "asset_depreciation_ids")
    util.remove_field(cr, "account.invoice.line", "asset_category_id")
    util.remove_field(cr, "account.invoice.line", "asset_mrr")
    util.remove_field(cr, "asset.modify", "method_end")
    util.remove_field(cr, "asset.modify", "asset_method_time")

    util.remove_field(cr, "product.template", "asset_category_id")
    util.remove_field(cr, "product.template", "deferred_revenue_category_id")

    util.remove_model(cr, "account.asset.category")
    util.remove_model(cr, "account.asset.depreciation.line")
    util.remove_model(cr, "asset.asset.report")
    util.remove_model(cr, "asset.depreciation.confirmation.wizard")
