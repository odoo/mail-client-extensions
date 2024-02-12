# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_model(cr, *eb("account.analytic.{group,plan}"))
    util.create_column(cr, "account_analytic_account", "root_plan_id", "int4")
    util.rename_field(cr, "account.analytic.account", "group_id", "plan_id")
    util.rename_field(cr, "account.analytic.line", "group_id", "plan_id")
    util.rename_xmlid(cr, *eb("analytic.account_analytic_{group,plan}_form_view"))
    util.rename_xmlid(cr, *eb("analytic.account_analytic_{group,plan}_tree_view"))
    util.rename_xmlid(cr, *eb("analytic.account_analytic_{group,plan}_action"))
    util.rename_xmlid(cr, *eb("analytic.analytic_{group,plan}_comp_rule"))
    util.rename_xmlid(cr, *eb("analytic.access_account_analytic_{group,plan}"))

    cr.execute(
        """INSERT INTO account_analytic_plan(name, complete_name, parent_path)
                       VALUES ('Default upg', 'Default upg', currval('account_analytic_plan_id_seq') || '/')
             RETURNING id
        """
    )
    default_plan_id = cr.fetchone()[0]
    query = """
        UPDATE account_analytic_account account
           SET plan_id = %s,
               root_plan_id = %s
         WHERE plan_id IS NULL
    """
    query = cr.mogrify(query, [default_plan_id, default_plan_id]).decode()
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_account", alias="account"))

    query = """
        UPDATE account_analytic_account account
           SET root_plan_id = split_part(plan.parent_path, '/', 1)::integer
          FROM account_analytic_plan plan
         WHERE plan.id = account.plan_id
           AND account.root_plan_id IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_account", alias="account"))

    query = """
        UPDATE account_analytic_line line
           SET plan_id = account.plan_id
          FROM account_analytic_account account
         WHERE account.id = line.account_id
           AND line.plan_id IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_line", alias="line"))

    query = """
        UPDATE account_analytic_account account
           SET company_id = NULL
          FROM account_analytic_line line
         WHERE account.id = line.account_id
           AND line.company_id != account.company_id
           AND account.company_id IS NOT NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_analytic_account", alias="account"))

    cr.execute(
        """
        SELECT 1
          FROM account_analytic_tag tag
     LEFT JOIN account_analytic_distribution distribution
            ON distribution.tag_id = tag.id
         WHERE distribution.id IS NULL
         LIMIT 1
    """
    )

    if cr.rowcount:
        cr.execute(
            """INSERT INTO account_analytic_plan(name, complete_name, parent_path)
                           VALUES ('Former Tag', 'Former Tag', currval('account_analytic_plan_id_seq') || '/')
                 RETURNING id
            """
        )
        util.ENVIRON["analytic_plan_former_tag"] = former_tag_plan_id = cr.fetchone()[0]

        util.create_column(cr, "account_analytic_account", "_tag", "int4")
        cr.execute(
            """
            WITH new_accounts AS (
                INSERT INTO account_analytic_account(_tag, name, company_id, plan_id, root_plan_id, active)
                SELECT tag.id, tag.name, tag.company_id, %s, %s, tag.active
                  FROM account_analytic_tag tag
             LEFT JOIN account_analytic_distribution distribution
                    ON distribution.tag_id = tag.id
                 WHERE distribution.id IS NULL
             RETURNING id, name, _tag
            ),
            _new_distribution AS (
                INSERT INTO account_analytic_distribution(account_id, tag_id, percentage)
                SELECT id, _tag, 100
                  FROM new_accounts
            )
            SELECT id, name
              FROM new_accounts
          ORDER BY name
         """,
            [former_tag_plan_id, former_tag_plan_id],
        )

        accounts = cr.dictfetchall()

        util.remove_column(cr, "account_analytic_account", "_tag")

        message = """
        <details>
        <summary>
            The analytic tags have been removed.
            Those without distribution have been transformed into analytic accounts to keep the information.
            They belong to a new plan named 'Former Tag'.
            If they were linked with Journal Items, analytic items for the new accounts have been created.
            It concerns the following accounts:
        </summary>
        <ul>{}</ul>
        </details>
        """.format(
            "\n".join(
                f"<li>{util.get_anchor_link_to_record('account.analytic.account', account['id'], account['name'])}</li>"
                for account in accounts
            )
        )
        util.add_to_migration_reports(category="Accounting", format="html", message=message)

    util.remove_field(cr, "account.analytic.line", "tag_ids")

    util.remove_record(cr, "analytic.group_analytic_tags")
