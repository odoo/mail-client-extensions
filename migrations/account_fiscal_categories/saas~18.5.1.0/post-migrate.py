def migrate(cr, version):
    cr.execute("""
        WITH accounts_per_rate AS (
             SELECT r.id AS rate_id,
                    r.rate,
                    r.date_from,
                    r.company_id,
                    ARRAY_AGG(a.id ORDER BY a.id) as account_ids
               FROM account_account_fiscal_rate r
               JOIN account_fiscal_category c
                 ON r.category_id = c.id
               JOIN account_account a
                 ON a.fiscal_category_id = c.id
           GROUP BY r.id
        ),
        updated AS (
             UPDATE account_account_fiscal_rate r
                SET related_account_id = accounts_per_rate.account_ids[1]
               FROM accounts_per_rate
              WHERE r.id = accounts_per_rate.rate_id
        )
        INSERT INTO account_account_fiscal_rate (rate, date_from, company_id, related_account_id)
             SELECT r.rate, r.date_from, r.company_id, unnest(r.account_ids[2:])
               FROM accounts_per_rate r
              WHERE cardinality(r.account_ids) > 1
    """)

    cr.execute("""
        DELETE FROM account_account_fiscal_rate
              WHERE related_account_id IS NULL
    """)
