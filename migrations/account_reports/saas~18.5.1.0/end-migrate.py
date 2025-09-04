def migrate(cr, version):
    # We need to wait for every return type of the localization to be created with their default values before we
    # can set the company-specific values.
    cr.execute("""
        WITH _deadlines AS (
             SELECT t.id,
                    jsonb_object_agg(c.id::text, t.default_deadline_days_delay) as delay
               FROM account_return_type t
         CROSS JOIN res_company c
              WHERE t.deadline_days_delay IS NULL
                AND t.default_deadline_days_delay IS NOT NULL
                AND COALESCE(t.country_id, c.fiscal_country_id) IS NOT DISTINCT FROM c.fiscal_country_id
           GROUP BY t.id
        )
        UPDATE account_return_type t
           SET deadline_days_delay = d.delay
          FROM _deadlines d
         WHERE d.id = t.id
    """)
