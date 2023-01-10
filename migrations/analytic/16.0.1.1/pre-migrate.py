# -*- coding: utf-8 -*-
import logging

from odoo.upgrade import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.analytic.16.0." + __name__)


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
                       VALUES ('Default', 'Default', currval('account_analytic_plan_id_seq') || '/')
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
           AND account.plan_id IS NULL
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

    util.remove_field(cr, "account.analytic.line", "tag_ids")

    # Get all fks from table res_groups
    fks = util.get_fk(cr, "res_groups")

    # Remove records referencing the group_analytic_tags from the referencing tables
    group_analytic_tags = util.ref(cr, "analytic.group_analytic_tags")
    standard_tables = ["ir_model_access", "rule_group_rel"]
    custom_tables = []
    for foreign_table, foreign_column, _, on_delete_action in fks:
        if on_delete_action == "r":
            if foreign_table not in standard_tables:
                cr.execute(
                    f'SELECT COUNT(*) FROM "{foreign_table}" WHERE "{foreign_column}" = %s',  # noqa:B907
                    (group_analytic_tags,),
                )
                count = cr.fetchone()[0]
                if count:
                    custom_tables.append((foreign_table, foreign_column, count))
                continue

            query = f'DELETE FROM "{foreign_table}" WHERE "{foreign_column}" = %s'  # noqa:B907
            query = cr.mogrify(query, (group_analytic_tags,)).decode()

            if util.column_exists(cr, foreign_table, "id"):
                util.parallel_execute(cr, util.explode_query_range(cr, query, table=foreign_table))
            else:
                cr.execute(query)

    if custom_tables:
        raise util.MigrationError(
            "The following 'table (column) - records count' are referencing the group 'analytic.group_analytic_tags'\n"
            "and cannot be removed automatically:\n"
            + "\n".join(f" - {table} ({column}) - {count} records" for table, column, count in custom_tables)
            + "\n Please remove them manually or remove the foreign key constraints set as RESTRICT."
        )

    util.remove_record(cr, "analytic.group_analytic_tags")
