from collections import defaultdict

from psycopg2 import sql
from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "workorder_count")
    analytic_util = util.import_script("analytic/saas~16.5.1.1/pre-migrate.py")

    project_plan_id = analytic_util.get_project_plan_id(cr)
    all_account_ids = set()
    res_ids_per_res_model_per_account_ids = defaultdict(lambda: defaultdict(list))

    cr.execute("""
        WITH prod_account AS (
                SELECT id res_id,
                       UNNEST(STRING_TO_ARRAY(STRING_AGG(key, ','), ',')::integer[]) AS account_id
                  FROM mrp_production,
                       JSONB_EACH_TEXT(analytic_distribution)
              GROUP BY id
                HAVING COUNT(*) = 1
                   AND SUM(value::numeric) = 100
        )
        SELECT pd.res_id,
               ARRAY_AGG(a.id)
          FROM prod_account pd
          -- join to filter out invalid ids
          JOIN account_analytic_account a
            ON pd.account_id = a.id
      GROUP BY pd.res_id
    """)
    for res_id, account_ids in cr.fetchall():
        res_ids_per_res_model_per_account_ids[tuple(sorted(account_ids))]["mrp_production"].append(res_id)
        all_account_ids.update(account_ids)

    cr.execute("""
          WITH _mrp_bom AS (
               SELECT CAST(SPLIT_PART(res_id, ',', 2) AS INTEGER) AS id,
                      CAST(value_text AS jsonb) AS analytic_distribution
                 FROM _ir_property
                WHERE name = 'analytic_distribution_text'
                  AND value_text != 'false'
          ),
          bom_account AS (
               SELECT id res_id,
                      UNNEST(STRING_TO_ARRAY(STRING_AGG(key, ','), ',')::integer[]) AS account_id
                 FROM _mrp_bom,
                      JSONB_EACH_TEXT(analytic_distribution)
             GROUP BY id
               HAVING COUNT(*) = 1
                  AND SUM(value::numeric) = 100.0
          )
          SELECT bom.res_id,
                 ARRAY_AGG(a.id)
            FROM bom_account bom
            -- join to filter out invalid ids
            JOIN account_analytic_account a
              ON bom.account_id = a.id
        GROUP BY bom.res_id
    """)
    for res_id, account_ids in cr.fetchall():
        res_ids_per_res_model_per_account_ids[tuple(sorted(account_ids))]["mrp_bom"].append(res_id)
        all_account_ids.update(account_ids)

    util.create_column(cr, "mrp_bom", "project_id", "integer")
    util.create_column(cr, "mrp_production", "project_id", "integer")

    if not res_ids_per_res_model_per_account_ids:
        return

    project_model = util.ref(cr, "project.model_project_project")
    task_model = util.ref(cr, "project.model_project_task")
    # create a mail alias per accounts group
    cr.execute(
        """
        INSERT INTO mail_alias (
                       alias_contact, alias_defaults,
                       alias_model_id, alias_parent_model_id,
                       alias_parent_thread_id
                    )
             SELECT 'followers', '{}',
                    %s, %s,
                    0
               FROM generate_series(1, %s)
          RETURNING id
        """,
        [task_model, project_model, len(res_ids_per_res_model_per_account_ids)],
    )
    new_mail_alias_ids = cr.fetchall()

    cr.execute(
        """
        SELECT account.id,
               SPLIT_PART(plan.parent_path, '/', 1)::integer AS root_plan_id
          FROM account_analytic_account account
          JOIN account_analytic_plan plan
            ON plan.id = account.plan_id
         WHERE account.id = ANY(%s)
        """,
        [list(all_account_ids)],
    )
    plan_id_per_account_id = dict(cr.fetchall())

    def get_col_name(plan_id):
        return "account_id" if plan_id == project_plan_id else f"x_plan{plan_id}_id"

    project_analytic_fnames = dict.fromkeys([get_col_name(plan_id) for plan_id in plan_id_per_account_id.values()])
    project_fnames = {
        **project_analytic_fnames,
        "name": None,
        "alias_id": None,
        "privacy_visibility": "followers",
        "rating_status": "stage",
        "rating_status_period": "monthly",
        "last_update_status": "to_define",
        "active": "false",
    }
    if util.module_installed(cr, "sale_timesheet"):
        project_fnames["billing_type"] = "not_billable"
    project_fvals_list = []

    cr.execute(
        """
        SELECT account.id,
               account.name->>'en_US'
          FROM account_analytic_account account
         WHERE account.id = ANY(%s)
        """,
        [list(all_account_ids)],
    )
    account_name_per_account_id = dict(cr.fetchall())

    for account_ids, (new_mail_alias_id,) in zip(res_ids_per_res_model_per_account_ids, new_mail_alias_ids):
        account_names = " | ".join([account_name_per_account_id[account_id] for account_id in account_ids])
        project_fvalues = tuple(
            {
                **project_fnames,
                "name": '{{"en_US": "Analytic Project ({})"}}'.format(account_names),
                "alias_id": new_mail_alias_id,
                **{get_col_name(plan_id_per_account_id[account_id]): account_id for account_id in account_ids},
            }.values()
        )
        project_fvals_list.append(project_fvalues)

    project_query = sql.SQL("INSERT INTO project_project ({fnames}) VALUES %s RETURNING id, {analytic_fnames}").format(
        fnames=sql.SQL(", ").join(map(sql.Identifier, project_fnames)),
        analytic_fnames=sql.SQL(", ").join(map(sql.Identifier, project_analytic_fnames)),
    )
    new_project_vals_list = execute_values(cr._obj, project_query, project_fvals_list, fetch=True)

    project_ids = [v[0] for v in new_project_vals_list]
    query = """
       WITH _to_update AS (
          SELECT id, alias_id FROM project_project WHERE id IN %s
       )
       UPDATE mail_alias a
          SET alias_defaults = '{"project_id": ' || u.id || '}',
              alias_parent_thread_id = u.id
         FROM _to_update u
        WHERE a.id = u.alias_id
    """
    cr.execute(query, [tuple(project_ids)])

    set_projects_queries = []
    for project_id, *account_ids in new_project_vals_list:
        sanitized_account_ids = tuple(sorted(filter(bool, account_ids)))
        res_ids_per_res_model = res_ids_per_res_model_per_account_ids[sanitized_account_ids]
        for res_model, res_ids in res_ids_per_res_model.items():
            set_projects_queries.append(
                cr.mogrify(
                    util.format_query(
                        cr,
                        "UPDATE {res_model} SET project_id = %(project_id)s WHERE id IN %(res_ids)s",
                        res_model=res_model,
                    ),
                    {"project_id": project_id, "res_ids": tuple(res_ids)},
                )
            )
    util.parallel_execute(cr, set_projects_queries)
