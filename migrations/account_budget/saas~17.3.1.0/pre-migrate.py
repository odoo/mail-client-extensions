from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    analytic_util = util.import_script("analytic/saas~16.5.1.1/pre-migrate.py")

    # Update budget state names and change "validate" to "confirmed"
    state_mapping = {
        "confirm": "confirmed",
        "validate": "confirmed",
        "cancel": "canceled",
    }
    util.change_field_selection_values(cr, "crossovered.budget", "state", state_mapping)
    util.change_field_selection_values(cr, "crossovered.budget.lines", "crossovered_budget_state", state_mapping)

    # budget post changes
    util.remove_model(cr, "account.budget.post", drop_table=False, ignore_m2m=("account_budget_rel",))
    util.remove_view(cr, "account_budget.view_budget_post_search")

    # budget analytic changes
    util.rename_model(cr, "crossovered.budget", "budget.analytic")
    util.rename_model(cr, "crossovered.budget.lines", "budget.line")
    util.rename_field(cr, "budget.analytic", "crossovered_budget_line", "budget_line_ids")
    # previous behavior was `both` but the new default is `expense`
    util.create_column(cr, "budget_analytic", "budget_type", "varchar", default="both")
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_,}budget_line_graph"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_,}budget_line_pivot"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_,}budget_line_form"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_,}budget_line_tree"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_,}budget_line_search"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_budget,budget_analytic}_search"))
    util.rename_xmlid(cr, *eb("account_budget.view_{crossovered_budget,budget_analytic}_kanban"))
    util.rename_xmlid(cr, *eb("account_budget.{crossovered_budget_view,view_budget_analytic}_tree"))
    util.rename_xmlid(cr, *eb("account_budget.{crossovered_budget_view,view_budget_analytic}_form"))

    # budget line changes
    util.remove_field(cr, "budget.line", "paid_date")
    util.remove_field(cr, "budget.line", "general_budget_id", drop_column=False)
    util.remove_field(cr, "budget.line", "analytic_plan_id")
    util.rename_field(cr, "budget.line", "analytic_account_id", "account_id")
    util.rename_field(cr, "budget.line", "crossovered_budget_id", "budget_analytic_id")
    util.rename_field(cr, "budget.line", "crossovered_budget_state", "budget_analytic_state")
    util.rename_field(cr, "budget.line", "percentage", "achieved_percentage")
    util.rename_field(cr, "budget.line", "practical_amount", "achieved_amount")
    util.rename_field(cr, "budget.line", "planned_amount", "budget_amount")

    # analytic account changes
    util.remove_field(cr, "account.analytic.account", "total_practical_amount")
    util.remove_field(cr, "account.analytic.account", "total_planned_amount")
    util.rename_field(cr, "account.analytic.account", "crossovered_budget_line", "budget_line_ids")

    # create analytic_json column in purchase_order_line
    util.create_column(cr, "purchase_order_line", "analytic_json", "jsonb")

    project_plan_id = analytic_util.get_project_plan_id(cr)
    cr.execute("SELECT id FROM account_analytic_plan WHERE id != %s AND parent_id IS NULL", [project_plan_id])
    other_plan_ids = [r[0] for r in cr.fetchall()]

    if other_plan_ids:
        analytic_util.create_analytic_plan_fields(cr, "budget.line", other_plan_ids)

        # Then move the value from the first column to the (new) correct one
        distributed_plans = ", ".join(
            f"CASE WHEN account.root_plan_id = {id_} THEN account.id ELSE NULL END AS plan{id_}_id"
            for id_ in other_plan_ids
        )
        query = f"""
            WITH updated_lines AS (
                SELECT line.id,
                       {distributed_plans},
                       CASE WHEN account.root_plan_id = {project_plan_id} THEN account.id ELSE NULL END AS account_id
                  FROM budget_line line
                  JOIN account_analytic_account account ON line.account_id = account.id
                 WHERE {{parallel_filter}}
            )
            UPDATE budget_line
               SET {", ".join(f"x_plan{id_}_id = updated_lines.plan{id_}_id" for id_ in other_plan_ids)},
                   account_id = updated_lines.account_id
              FROM updated_lines
             WHERE updated_lines.id = budget_line.id
        """
        util.explode_execute(cr, query, "budget_line", alias="line")

        # create new model for budget.report and add new fields to it
        cr.execute("""
            INSERT INTO ir_model(name, "order", model)
            VALUES (jsonb_build_object('en_US', 'Budget Report'), 'False', 'budget.report')
            RETURNING id
        """)

        model_id = cr.fetchone()[0]
        cr.execute(
            """
            INSERT INTO ir_model_fields(name, model, model_id, field_description,
                                        state, store, ttype, relation)
                 SELECT 'x_plan' || plan.id ||'_id', 'budget.report', %s, plan.name,
                        'manual', true, 'many2one', 'account.analytic.account'
                   FROM account_analytic_plan plan
                  WHERE plan.id = ANY(%s)
        """,
            [model_id, other_plan_ids],
        )

        analytic_util.create_analytic_plan_indexes(cr, "budget.line", other_plan_ids)
