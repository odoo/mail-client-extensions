from psycopg2 import sql
from psycopg2.extras import Json

from odoo.upgrade import util


def migrate(cr, version):
    # Retrieve the project plan id and all the other plan ids
    cr.execute(
        r"""
        SELECT ARRAY_AGG(value::int ORDER BY value::int)
          FROM ir_config_parameter
         WHERE key LIKE 'default\_analytic\_plan\_id\_%'
        """
    )
    all_project_plans = cr.fetchone()[0] or []
    project_plan_id = all_project_plans[0] if all_project_plans else _find_or_create_project_plan(cr)
    if project_plan_id not in all_project_plans:
        all_project_plans.append(project_plan_id)

    cr.execute("SELECT id FROM account_analytic_plan WHERE id != %s AND parent_id IS NULL", [project_plan_id])
    other_plan_ids = [r[0] for r in cr.fetchall()]
    cr.execute(
        r"""
        DELETE FROM ir_config_parameter
              WHERE key LIKE 'default\_analytic\_plan\_id\_%%';
        INSERT INTO ir_config_parameter (key, value)
             VALUES ('analytic.project_plan', %s)
    """,
        [project_plan_id],
    )

    # Make analytic plans shared between companies, except for some fields
    # First merge plans with the same name, most likely from different companies
    cr.execute(
        """
        SELECT ARRAY_AGG(id)
          FROM account_analytic_plan
      GROUP BY complete_name
        HAVING COUNT(*) > 1
    """
    )
    mapping = {}
    project_group = set(all_project_plans or [])
    for [group] in cr.fetchall():
        if set(group) & project_group:
            project_group.update(group)  # merge project plans even if they have a different name
        else:
            mapping.update(dict.fromkeys(group[1:], group[0]))
    # Process the project plans last
    mapping.update(dict.fromkeys((i for i in project_group if i != project_plan_id), project_plan_id))
    if mapping:
        util.replace_record_references_batch(cr, mapping, "account.analytic.plan")
        cr.execute("DELETE FROM account_analytic_plan WHERE id = ANY(%s)", [list(mapping)])

    util.remove_record(cr, "analytic.analytic_plan_comp_rule")
    util.convert_field_to_property(
        cr,
        model="account.analytic.plan",
        field="default_applicability",
        type="selection",
        default_value="optional",
    )
    columns = util.get_columns(cr, "account_analytic_applicability")
    util.create_column(
        cr, "account_analytic_applicability", "company_id", "int4", fk_table="res_company", on_delete_action="SET NULL"
    )
    query = util.format_query(
        cr,
        """
        WITH applicability AS (
            SELECT min(id) AS id
              FROM account_analytic_applicability
          GROUP BY applicability, business_domain, analytic_plan_id
        )
        INSERT INTO account_analytic_applicability ({}, company_id)
             SELECT {}, company.id
               FROM account_analytic_applicability aaa
               JOIN applicability a
                 ON a.id = aaa.id,
                    res_company company;

        DELETE FROM account_analytic_applicability
              WHERE company_id IS NULL;
        """,
        columns,
        columns.using(alias="aaa"),
    )
    cr.execute(query)

    util.remove_field(cr, "account.analytic.plan", "company_id")

    # Split account on multiple columns (one by plan)
    # If we have an invoice line with a distribution like this (1 and 2 in the same plan, a in another plan, and i in another)
    # | All P | Perc% |
    # |-------|-------|
    # |     1 |    50 |
    # |     2 |    50 |
    # |     a |   100 |
    # |     i |   100 |
    #
    # It should become this
    # | Plan A | Plan B | Plan C | Perc% |
    # |--------|--------|--------|-------|
    # |      1 |        |        |    50 |
    # |      2 |        |        |    50 |
    # |        |      a |        |   100 |
    # |        |        |      i |   100 |
    cr.execute("ALTER TABLE account_analytic_line ALTER COLUMN account_id DROP NOT NULL")

    if other_plan_ids:
        create_analytic_plan_fields(cr, "account.analytic.line", other_plan_ids)
        # Now move the value from the first column to the (new) correct one
        distributed_plans = [
            util.format_query(
                cr,
                "{} = CASE WHEN plan.parent_path LIKE %s THEN account.id ELSE NULL END",
                f"x_plan{id_}_id",
            )
            for id_ in other_plan_ids
        ]
        query = cr.mogrify(
            util.format_query(
                cr,
                """
                UPDATE account_analytic_line line
                   SET account_id = CASE WHEN plan.parent_path LIKE %s THEN account.id ELSE NULL END,
                       {distributed_plans}
                  FROM account_analytic_account account,
                       account_analytic_plan plan
                 WHERE account.id = line.account_id
                   AND plan.id = line.plan_id
                """,
                distributed_plans=sql.SQL(", ").join(map(sql.SQL, distributed_plans)),
            ),
            [f"{id_}/%" for id_ in [project_plan_id, *other_plan_ids]],
        ).decode()
        util.explode_execute(cr, query, table="account_analytic_line", alias="line")
        create_analytic_plan_indexes(cr, "account.analytic.line", other_plan_ids)

    util.remove_field(cr, "account.analytic.line", "plan_id")


def _find_or_create_project_plan(cr):
    cr.execute("SELECT id FROM account_analytic_plan WHERE parent_id IS NUll ORDER BY id FETCH FIRST ROW ONLY")
    [plan_id] = cr.fetchone() or [None]
    if not plan_id:
        cr.execute(
            """INSERT INTO account_analytic_plan(name, default_applicability)
                           VALUES (%s, 'optional')
                 RETURNING id
            """,
            [
                Json({"en_US": "Default"})
                if util.column_type(cr, "account_analytic_plan", "name") == "jsonb"
                else "Default"
            ],
        )
        plan_id = cr.fetchone()[0]
    return plan_id


def get_project_plan_id(cr):
    cr.execute("SELECT value::int FROM ir_config_parameter WHERE key = 'analytic.project_plan'")
    if cr.rowcount:
        return cr.fetchone()[0]
    return _find_or_create_project_plan(cr)


def create_analytic_plan_fields(cr, model, other_plan_ids):
    # Create the new fields/columns
    table = util.table_of_model(cr, model)
    if other_plan_ids:
        plan_name = util.SQLStr(
            "plan.name"
            if util.column_type(cr, "account_analytic_plan", "name") == "jsonb"
            else "jsonb_build_object('en_US', plan.name)"
        )
        query = util.format_query(
            cr,
            """
                INSERT INTO ir_model_fields(name, model, model_id, field_description,
                                            state, store, ttype, relation)
                     SELECT 'x_plan' || plan.id ||'_id', model, m.id, {plan_name},
                            'manual', true, 'many2one', 'account.analytic.account'
                       FROM account_analytic_plan plan,
                            ir_model m
                      WHERE plan.id = ANY(%s)
                        AND m.model = %s
            """,
            plan_name=plan_name,
        )
        cr.execute(query, [other_plan_ids, model])

        for id_ in other_plan_ids:
            util.create_column(
                cr,
                table,
                f"x_plan{id_}_id",
                "int4",
                fk_table="account_analytic_account",
                on_delete_action="SET NULL",
            )


def create_analytic_plan_indexes(cr, model, other_plan_ids):
    """Create the indexes on the plan fields"""
    table = util.table_of_model(cr, model)
    util.parallel_execute(
        cr,
        [
            util.format_query(
                cr,
                "CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} USING btree ({column}) WHERE {column} IS NOT NULL",
                index_name=util.fields.make_index_name(table, f"x_plan{id_}_id"),
                table_name=table,
                column=f"x_plan{id_}_id",
            )
            for id_ in other_plan_ids
        ],
    )
