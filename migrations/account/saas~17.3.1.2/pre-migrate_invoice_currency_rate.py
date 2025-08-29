from collections import defaultdict

from psycopg2 import sql

from odoo.upgrade import util


def _build_currency_table_query(cr, company_id, currency_id, first_rate_date, last_rate_date):
    if company_id is None:
        company_id_condition = "company_id IS NULL"
        rate_fallback = 1  # There is no rate for a specific day for currency_id with or without company_id
    else:
        company_id_condition = "company_id = %(company_id)s"
        rate_fallback = None  # NULL since we will first try to search for a rate (of currency_id) without company_id
    query = util.format_query(
        cr,
        # On CTE `info` below:
        # Each rate is valid for a date range (from_day to to_day).
        # But res_currency_rate only associates the start date with each rate.
        # The day before this start date is the last day the (chronologically) previous rate is valid.
        # Here we basically associate each date in res_curency_rate with the rate that ends there and the start date of the rate.
        # We are only interested in the rates inside the conversion window (first_rate_date to last_rate_date).
        # Thus the first / last rate in the conversion window require some additional care (see comments in the query);
        # the problem is that they start / end (respectively) outside the conversion window.
        """
         WITH start_rate AS (
             SELECT rate
               FROM res_currency_rate
              WHERE name <= %(first_rate_date)s
                AND {company_id_condition}
                AND currency_id = %(currency_id)s
              ORDER BY name DESC
              LIMIT 1
         ), info AS (
             SELECT COALESCE(lag(rate) over(ORDER BY name ASC), -- take the previous rate inside the conversion window
                             (SELECT rate FROM start_rate), -- take the last rate before the conversion window
                             %(rate_fallback)s::numeric) -- there is no rate before the conversion window
                        AS rate,
                    COALESCE(lag(name) over(ORDER BY name ASC), %(first_rate_date)s) AS from_day,
                    name - interval '1 day' AS to_day
               FROM (   SELECT rate, name FROM res_currency_rate
                         WHERE {company_id_condition}
                           AND currency_id = %(currency_id)s
                           AND name >= %(first_rate_date)s
                           AND name <= %(last_rate_date)s
                     UNION ALL -- Add a row to end the last rate (from inside the conversion window; or possibly the first rate)
                               (VALUES (NULL::numeric, %(last_rate_date)s + interval '1 day'))
                    ) rates
         )
         INSERT INTO _upg_currency_rates
             SELECT %(company_id)s,
                    %(currency_id)s,
                    rate,
                    generate_series(
                        from_day::timestamp without time zone,
                        to_day::timestamp without time zone,
                        '1 day'
                    )::date
               FROM info
        """,
        company_id_condition=util.SQLStr(company_id_condition),
    )
    return cr.mogrify(
        query,
        {
            "currency_id": currency_id,
            "company_id": company_id,
            "first_rate_date": first_rate_date,
            "last_rate_date": last_rate_date,
            "rate_fallback": rate_fallback,
        },
    )


def migrate(cr, version):
    # A new computed stored field invoice_currency_rate was added to model 'account.move'.
    # It is computed here.
    # The column 'l10n_dk_currency_rate_at_transaction' of 'account.move' is dropped.
    # This finishes the removal of module 'l10n_dk_bookkeeping that was started in the migration of base.

    # Now all invoice_line_ids belonging to a move use the exchange rate of that move (invoice_currency_rate).
    # In previous versions different lines from invoice_line_ids could use different rates.
    # As a workaround we compute the conversion rate for old invoices as follows (use the first method that is possible)
    # In a first query (c.f. `new_rate_expression`):
    #   1. Set it to 1 in some trivial cases (e.g. if the move currency is the company currency)
    #   2. Take it from fields (removed after this upgrade) that stored it already.
    #   3. Compute it from the ratio of the totals of the invoice in company and document currency
    # In a second query for all the remaining moves (c.f. `update_query_remaining_invoices`):
    #   4. Fetch the rate from the database at invoice date (or other dates depending on localization)
    #      (see `move_invoice_rate_date_expression`)

    util.create_column(cr, "account_move", "invoice_currency_rate", "numeric")

    extra_where_ORs = []
    extra_cases = []
    # Setup special handling for l10n_ar.
    if util.column_exists(cr, "account_move", "l10n_ar_currency_rate"):
        condition = "(COALESCE(country.code, '') = 'AR' AND COALESCE(move.l10n_ar_currency_rate, 0) <> 0)"
        extra_where_ORs.append(f"OR {condition}")
        extra_cases.append(f"WHEN {condition} THEN 1 / move.l10n_ar_currency_rate")
    # Setup special handling for l10n_dk_bookkeeping.
    l10n_dk_bookkeeping = util.column_exists(cr, "account_move", "l10n_dk_currency_rate_at_transaction")
    if l10n_dk_bookkeeping:
        condition = "(COALESCE(country.code, '') = 'DK' AND move.l10n_dk_currency_rate_at_transaction IS NOT NULL)"
        extra_where_ORs.append(f"OR {condition}")
        extra_cases.append(f"WHEN {condition} THEN move.l10n_dk_currency_rate_at_transaction")
    extra_where_ORs = "\n".join(extra_where_ORs)
    extra_cases = "\n".join(extra_cases)

    # This query does not necessarily upgrade all invoices.
    # I.e multi-currency invoices where amount_total_signed is NULL or 0 is excluded
    # (up to special handling for l10n_ar and l10n_dk_bookkeeping).
    # The remaining invoices are upgraded later (if there are any).
    query = f"""
        WITH to_update AS (
               SELECT move.id,
                      CASE
                           WHEN    move.currency_id IS NULL
                                OR move.company_id IS NULL
                                OR company.currency_id IS NULL
                                OR move.currency_id = company.currency_id
                           THEN 1
                           {extra_cases}
                           ELSE ABS(move.amount_total / move.amount_total_signed)
                       END AS rate
                 FROM account_move move
            LEFT JOIN res_company company
                   ON move.company_id = company.id
            LEFT JOIN res_country country
                   ON company.account_fiscal_country_id = country.id
                WHERE move.move_type <> 'entry' -- Only invoices (incl. receipts) in foreign currency are relevant
                  AND (   move.company_id IS NULL -- no company set
                       OR move.currency_id = company.currency_id -- company set and same currency
                       {extra_where_ORs}
                       OR COALESCE(move.amount_total_signed, 0) <> 0)
                   AND {{parallel_filter}}
        ) UPDATE account_move move
             SET invoice_currency_rate = to_update.rate
            FROM to_update
           WHERE move.id = to_update.id
    """
    util.explode_execute(cr, query, table="account_move", alias="move")

    # The module 'l10n_dk_bookkeeping' was removed during the upgrade of module 'base' already.
    # But the column was kept so that we can use it for this script.
    if l10n_dk_bookkeeping:
        util.remove_column(cr, "account_move", "l10n_dk_currency_rate_at_transaction")

    # Some localizations have special requirements on the date used for the the currency conversion.
    # The date we use is the first non-NULL result of expressions in `date_expressions`
    # (also see variable `move_invoice_rate_date_expression`).
    date_expressions = []
    if util.module_installed(cr, "l10n_cz"):
        date_expressions.append("CASE WHEN country.code = 'CZ' THEN move.taxable_supply_date END")
    if util.module_installed(cr, "l10n_hu_edi"):
        date_expressions.append("CASE WHEN country.code = 'HU' THEN move.delivery_date END")
    date_expressions.extend(
        [
            "move.invoice_date",
            "move.date",
            "(NOW() at time zone 'UTC')::date",
        ]
    )
    move_invoice_rate_date_expression = sql.SQL(
        util.format_query(cr, "COALESCE({})", sql.SQL(",\n").join(map(sql.SQL, date_expressions)))
    )

    # Check whether all invoices are upgraded already.
    # In the process we already gather some information needed to upgrade the remaining invoices:
    # The information will later be used to build a table called _upg_currency_rates in which we can quickly
    # lookup the invoice_currency_rate of the remaining invoices.
    # (See the comments there for more details.)
    remaining_currencies_query = util.format_query(
        cr,
        """
          SELECT split_part(company.parent_path, '/', 1)::integer AS root_company_id,
                 unnest(ARRAY[move.currency_id, company.currency_id]) AS currency,
                 MIN({move_invoice_rate_date_expression}) AS first_rate_date,
                 MAX({move_invoice_rate_date_expression}) AS last_rate_date
            FROM account_move move
            JOIN res_company company
              ON move.company_id = company.id
       LEFT JOIN res_country country
              ON company.account_fiscal_country_id = country.id
           WHERE move.move_type <> 'entry'
             AND move.invoice_currency_rate IS NULL
        GROUP BY 1, 2
        """,
        move_invoice_rate_date_expression=move_invoice_rate_date_expression,
    )
    cr.execute(remaining_currencies_query)
    remaining_currencies = cr.fetchall()
    if remaining_currencies:
        _upgrade_remaining_currencies(cr, remaining_currencies, move_invoice_rate_date_expression)


def _upgrade_remaining_currencies(cr, remaining_currencies, move_invoice_rate_date_expression):
    # Upgrade the remaining invoices

    # To be consistent with `_get_rates` from model `res.currency`:
    #   * We do not consider the rates for the company itself but the ones for `company.root_id`.
    #     In fact we only compute the rates for root companies; remaining_currencies only contains information about root companies.
    #   * Rates without `company_id` are only used when they start before the first rate with a `company_id'
    #     (for a given pair of compmany, currency).
    cr.execute("""
        DROP TABLE IF EXISTS _upg_currency_rates;
        CREATE UNLOGGED TABLE _upg_currency_rates (
            root_company_id     integer,
            currency_id         integer  NOT NULL,
            rate                numeric,
            date                date     NOT NULL
        );
    """)
    currency_rates_queries = []

    # Gather queries inserting rates that have a company_id (and gather data per currency independent of company)
    currency_data = defaultdict(list)
    for company_id, currency_id, first_rate_date, last_rate_date in remaining_currencies:
        currency_rates_queries.append(
            _build_currency_table_query(cr, company_id, currency_id, first_rate_date, last_rate_date)
        )
        current = currency_data.get(currency_id, (first_rate_date, last_rate_date))
        currency_data[currency_id] = (min(current[0], first_rate_date), max(current[1], last_rate_date))

    # Gather queries inserting rates that do not have a company_id
    currency_rates_queries.extend(
        _build_currency_table_query(cr, None, currency_id, first_conversion_date, last_conversion_date)
        for currency_id, (first_conversion_date, last_conversion_date) in currency_data.items()
    )

    util.parallel_execute(cr, currency_rates_queries)
    cr.execute("""
        CREATE UNIQUE INDEX ON _upg_currency_rates (root_company_id, currency_id, date) INCLUDE (rate);
        ANALYZE _upg_currency_rates;
    """)

    update_query_remaining_invoices = util.format_query(
        cr,
        """
        WITH to_update AS (
            SELECT move.id,
                   COALESCE(foreign_rate.rate, foreign_rate_without_company.rate)
                       / COALESCE(company_rate.rate, company_rate_without_company.rate) AS rate
              FROM account_move move
              JOIN res_company company
                ON company.id = move.company_id
         LEFT JOIN res_country country
                ON company.account_fiscal_country_id = country.id
              JOIN _upg_currency_rates foreign_rate
                ON foreign_rate.root_company_id = (split_part(company.parent_path, '/', 1)::integer)
               AND foreign_rate.currency_id = move.currency_id
               AND foreign_rate.date = ({move_invoice_rate_date_expression})
              JOIN _upg_currency_rates company_rate
                ON company_rate.root_company_id = (split_part(company.parent_path, '/', 1)::integer)
               AND company_rate.currency_id = company.currency_id
               AND company_rate.date = ({move_invoice_rate_date_expression})
              JOIN _upg_currency_rates foreign_rate_without_company
                ON foreign_rate_without_company.root_company_id IS NULL
               AND foreign_rate_without_company.currency_id = move.currency_id
               AND foreign_rate_without_company.date = ({move_invoice_rate_date_expression})
              JOIN _upg_currency_rates company_rate_without_company
                ON company_rate_without_company.root_company_id IS NULL
               AND company_rate_without_company.currency_id = company.currency_id
               AND company_rate_without_company.date = ({move_invoice_rate_date_expression})
             WHERE {{parallel_filter}}
               AND move.move_type <> 'entry'
               AND move.invoice_currency_rate IS NULL
        )
        UPDATE account_move move
           SET invoice_currency_rate = to_update.rate
          FROM to_update
         WHERE move.id = to_update.id
        """,
        move_invoice_rate_date_expression=move_invoice_rate_date_expression,
    )
    util.explode_execute(cr, update_query_remaining_invoices, table="account_move", alias="move")

    cr.execute("DROP TABLE _upg_currency_rates")
