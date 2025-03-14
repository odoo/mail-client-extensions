from odoo.upgrade import util


def migrate(cr, version):
    util.alter_column_type(
        cr, "account_report", "filter_account_type", "varchar", using="CASE WHEN {0} THEN 'both' ELSE 'disabled' END"
    )
    util.remove_view(cr, "account.view_account_analytic_line_filter_inherit")

    cr.execute("DROP INDEX IF EXISTS account_move_line__unreconciled_index")
    cr.execute(
        """
        CREATE INDEX "account_move_line__unreconciled_index"
                  ON "account_move_line"
               USING btree (account_id, partner_id)
                  -- Match exactly how the ORM converts domains to ensure the query planner uses it
               WHERE (reconciled IS NULL OR reconciled = false OR reconciled IS NOT true) AND parent_state = 'posted'
    """
    )

    util.convert_field_to_translatable(cr, "account.reconcile.model.line", "label")

    cr.execute(
        """
        SELECT ARRAY_AGG(id ORDER BY active DESC, id) AS ids
          FROM account_account_tag
      GROUP BY name, applicability, country_id
        HAVING COUNT(*) > 1

        """
    )
    if cr.rowcount:
        dupes = {x: t[0] for (t,) in cr.fetchall() for x in t[1:]}
        util.replace_record_references_batch(cr, dupes, "account.account.tag", replace_xmlid=False)
        cr.execute("DELETE FROM account_account_tag WHERE id IN %s", [tuple(dupes.keys())])

    util.remove_field(cr, "account.full.reconcile", "name")
    util.delete_unused(cr, "account.sequence_reconcile_seq")

    util.create_column(cr, "account_move_line", "invoice_date", "date")
    util.explode_execute(
        cr,
        """
        UPDATE account_move_line l
           SET invoice_date = m.invoice_date
          FROM account_move m
         WHERE m.id = l.move_id
           AND m.invoice_date IS DISTINCT FROM l.invoice_date
        """,
        table="account_move_line",
        alias="l",
    )

    util.explode_execute(
        cr,
        """
        UPDATE account_move_line
           SET matching_number = full_reconcile_id::varchar
         WHERE full_reconcile_id IS NOT NULL
        """,
        table="account_move_line",
    )

    cr.execute("""
        /*
        Create and join graphs for all partial reconciliations.
        Each `account_partial_reconcile` is an edge between 2 `account_move_line` nodes.
        `matching` represents the link between each node and it's graph number (matching  number),
        where the graph number is the minimam id of the partial reconcile.
        */
        CREATE UNLOGGED TABLE matching (min_id integer, line_id integer);
        CREATE INDEX matching_min_id_idx ON matching USING btree (min_id);
        CREATE INDEX matching_line_id_idx ON matching USING btree (line_id);

        DO $$
        DECLARE
            r record;
            debit_min_id integer;
            credit_min_id integer;
        BEGIN
            FOR r IN SELECT id, debit_move_id, credit_move_id
                       FROM account_partial_reconcile
                      WHERE full_reconcile_id IS NULL
                   ORDER BY id
            LOOP
                SELECT min_id INTO debit_min_id FROM matching WHERE line_id = r.debit_move_id;
                SELECT min_id INTO credit_min_id FROM matching WHERE line_id = r.credit_move_id;
                IF debit_min_id IS NOT NULL AND credit_min_id IS NOT NULL THEN
                    IF credit_min_id != debit_min_id THEN  -- merge graphs
                        UPDATE matching
                           SET min_id = LEAST(credit_min_id, debit_min_id)
                         WHERE min_id IN (credit_min_id, debit_min_id)
                           AND min_id != LEAST(credit_min_id, debit_min_id);
                    END IF;
                ELSIF debit_min_id IS NOT NULL THEN  -- add node to graph
                    INSERT INTO matching (min_id, line_id) VALUES (debit_min_id, r.credit_move_id);
                ELSIF credit_min_id IS NOT NULL THEN  -- add node to graph
                    INSERT INTO matching (min_id, line_id) VALUES (credit_min_id, r.debit_move_id);
                ELSE  -- create new graph
                    INSERT INTO matching (min_id, line_id) VALUES (r.id, r.debit_move_id), (r.id, r.credit_move_id);
                END IF;
            END LOOP;
        END$$
    """)
    cr.execute("ANALYZE matching")
    util.explode_execute(
        cr,
        """
            UPDATE account_move_line line
               SET matching_number = 'P' || matching.min_id
              FROM matching
             WHERE matching.line_id = line.id
        """,
        table="account_move_line",
        alias="line",
    )
    cr.execute("DROP TABLE matching")

    # ANALYTIC
    # Merge lines that can be merged when all the plans are at 100% and at most one plan is split on multiple accounts
    cr.execute(
        """
        SELECT value::int
          FROM ir_config_parameter
         WHERE key = 'analytic.project_plan'
    """
    )
    [project_plan_id] = cr.fetchone()
    cr.execute("SELECT id FROM account_analytic_plan WHERE id != %s AND parent_id IS NULL", [project_plan_id])
    other_plan_ids = [r[0] for r in cr.fetchall()]
    column_names = ["account_id"] + [f"x_plan{id_}_id" for id_ in other_plan_ids]

    # If we have an invoice line with a distribution like this
    # | Plan A | Plan B | Plan C | Perc% |
    # |--------|--------|--------|-------|
    # |      1 |        |        |    50 |
    # |      2 |        |        |    50 |
    # |        |      a |        |   100 |
    # |        |        |      i |   100 |
    #
    # We can merge it like this
    # | Plan A | Plan B | Plan C | Perc% |
    # |--------|--------|--------|-------|
    # |      1 |      a |      i |    50 |
    # |      2 |      a |      i |    50 |
    accounts_per_plan_compute = ",\n                    ".join(
        f"ARRAY_AGG(al.{col}) FILTER (WHERE al.{col} IS NOT NULL) AS {col}s" for col in column_names
    )
    where_multiple_account_per_plan = "\n                         ".join(
        f"WHEN COUNT(DISTINCT al.{col}) > 1 THEN ARRAY_AGG(al.id) FILTER (WHERE al.{col} IS NOT NULL)"
        for col in column_names
    )
    count_multiple_accounts_per_plan = " + ".join(f"(COUNT(DISTINCT al.{col}) > 1)::int" for col in column_names)
    unchanged_distribution = "AND ".join(
        f"""COALESCE(SUM((ml.analytic_distribution->>al.{col}::text)::numeric) = 100, True)  -- only 100% or not used
                AND COALESCE(SUM(al.amount) FILTER (WHERE al.{col} IS NOT NULL) = -ml.balance, True)  -- unchanged distribution or not used
                """
        for col in column_names
    )
    update_fields = ",\n                    ".join(
        f"{col} = CASE WHEN ARRAY_LENGTH(raw.{col}s, 1) = 1 THEN raw.{col}s[1] ELSE al.{col} END"
        for col in column_names
    )
    query = f"""
        /*
            `raw` contains all the analytic lines linked to a account move line that can be merged into a single analytic line
            We consider that it can be merged into a single line if
              - there is at most one plan split over multiple accounts
              - the distribution amounts for 100% of the account move line
              - it was not modified manually on the analytic lines
        */
        WITH raw AS (
             SELECT {accounts_per_plan_compute},
                    CASE
                         {where_multiple_account_per_plan}
                         ELSE ARRAY_AGG(al.id) FILTER (WHERE al.account_id IS NOT NULL)
                    END AS to_update,  -- update the rows split on multiple accounts if any (maximum one plan split)
                    ARRAY_AGG(al.id) AS all_lines
               FROM account_analytic_line al
               JOIN account_move_line ml ON ml.id = al.move_line_id
              WHERE {{parallel_filter}}
           GROUP BY ml.id
                    -- there is at most one plan split on multiple accounts
             HAVING ({count_multiple_accounts_per_plan}) <= 1
                    -- the distribution is 100% and not modified manually
                AND {unchanged_distribution}
        ),
        updating AS (
             UPDATE account_analytic_line al
                SET {update_fields}
               FROM raw
              WHERE al.id = ANY(raw.to_update)
        )
        DELETE FROM account_analytic_line al
              USING raw
              WHERE al.id = ANY(raw.all_lines)
                AND al.id != ALL(raw.to_update)
    """
    util.explode_execute(cr, query, "account_move_line", alias="ml")
