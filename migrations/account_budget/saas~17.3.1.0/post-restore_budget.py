from odoo.upgrade import util


def migrate(cr, version):
    # The new plan for budgetary positions needs to be created
    # with the use of ORM to ensure that it's set up correctly.
    plan = util.env(cr)["account.analytic.plan"].create(
        {"name": "Upgraded Budget Plan", "description": "Analytic plan for upgraded budgetary positions."}
    )

    cr.execute("ALTER TABLE account_analytic_account ADD COLUMN _budget_post int4")

    cr.execute(
        util.format_query(
            cr,
            """
              WITH analytic_accounts AS (
                       INSERT INTO account_analytic_account (name, plan_id, root_plan_id, active, company_id, _budget_post)
                            SELECT jsonb_build_object('en_US', pos.name),
                                   %(plan_id)s,
                                   %(plan_id)s,
                                   't',
                                   pos.company_id,
                                   pos.id
                              FROM account_budget_post pos
                         RETURNING id, company_id, _budget_post
                   ),
                   insert_distribution_model AS (
                       INSERT INTO account_analytic_distribution_model (company_id, analytic_distribution, account_prefix)
                            SELECT aa.company_id,
                                   jsonb_build_object(aa.id, 100),
                                   account.code
                              FROM analytic_accounts aa
                              JOIN account_budget_rel rel
                                ON aa._budget_post = rel.budget_id
                              JOIN account_account account
                                ON rel.account_id = account.id
                   ),
                   update_budget_line AS (
                       UPDATE budget_line
                          SET {plan_col} = aa.id
                         FROM analytic_accounts aa
                        WHERE budget_line.general_budget_id = aa._budget_post
                   ),
                   new_distribution AS (
                       SELECT aml.id,
                              JSONB_OBJECT_AGG(
                                  distribution.accounts|| ',' || aa.id,
                                  distribution.percent
                              ) as distribution
                         FROM account_move_line aml
                         JOIN account_budget_rel rel
                           ON aml.account_id = rel.account_id
                         JOIN analytic_accounts aa
                           ON aa._budget_post = rel.budget_id
                   CROSS JOIN JSONB_EACH(aml.analytic_distribution) AS distribution(accounts, percent)
                     GROUP BY aml.id
                   ),
                   update_move_line AS (
                       UPDATE account_move_line aml
                          SET analytic_distribution = new_distribution.distribution
                         FROM new_distribution
                        WHERE new_distribution.id = aml.id
                   )
            UPDATE account_analytic_line aal
               SET {plan_col} = aa.id
              FROM account_move_line aml
              JOIN account_budget_rel rel
                ON aml.account_id = rel.account_id
              JOIN analytic_accounts aa
                ON aa._budget_post = rel.budget_id
             WHERE aal.move_line_id = aml.id
            """,
            plan_col=plan._strict_column_name(),
        ),
        {
            "plan_id": plan.id,
        },
    )

    cr.execute(
        """
        DROP TABLE account_budget_rel CASCADE;
        ALTER TABLE budget_line DROP COLUMN general_budget_id CASCADE;
        ALTER TABLE account_analytic_account DROP COLUMN _budget_post CASCADE;
        """
    )
