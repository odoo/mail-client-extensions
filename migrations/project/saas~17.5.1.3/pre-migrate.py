from odoo.upgrade import util


def migrate(cr, version):
    analytic_util = util.import_script("analytic/saas~16.5.1.1/pre-migrate.py")

    project_plan_id, _all_project_plans = analytic_util.get_all_analytic_plan_ids(cr)
    cr.execute("SELECT id FROM account_analytic_plan WHERE id != %s AND parent_id IS NULL", [project_plan_id])
    other_plan_ids = [r[0] for r in cr.fetchall()]
    analytic_util.create_analytic_plan_fields(cr, "project.project", other_plan_ids)

    queries = [
        f"""
        UPDATE project_project project
           SET x_plan{_id}_id = project.analytic_account_id
          FROM account_analytic_account account
          JOIN account_analytic_plan plan
            ON plan.id = account.root_plan_id
           AND plan.id = {_id}
         WHERE project.analytic_account_id = account.id
    """
        for _id in other_plan_ids
    ]
    util.parallel_execute(cr, queries)

    util.rename_field(cr, "project.project", "analytic_account_id", "account_id")

    util.remove_field(cr, "project.task", "analytic_account_id")
    util.remove_field(cr, "res.config.settings", "analytic_plan_id")
