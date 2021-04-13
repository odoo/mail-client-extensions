# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # column used in `end-` script
    ignore = ("id", "parent_id", "parent_path", "company_id")
    cols = util.get_columns(cr, "account_group", ignore, ["ag"])

    # Old groups use as template to create group per company
    cr.execute("SELECT id from account_group")
    old_groups_ids = tuple(g[0] for g in cr.fetchall())

    if old_groups_ids:
        # All groups will be duplicated for all companies that have at least one group
        cols_str = ",".join(cols[0])
        cols_with_pre_fix = ",".join(cols[1])
        cr.execute(
            f"""
            WITH RECURSIVE parent_tree(id, parent_ids) AS (
                 SELECT ag.id, array_agg(ag.id)
                   FROM account_group ag
                  WHERE ag.parent_id IS NULL
                  GROUP BY ag.id
            UNION ALL
                 SELECT ag.id, array_append(p_t.parent_ids, ag.id)
                   FROM account_group ag
                   JOIN parent_tree p_t ON  ag.parent_id = p_t.id
            )
            INSERT INTO account_group (company_id, {cols_str})
                 SELECT a.company_id, {cols_with_pre_fix}
                   FROM parent_tree p_t
                   JOIN account_group ag ON ag.id = ANY(p_t.parent_ids)
                   JOIN account_account a ON a.group_id = ANY(p_t.parent_ids)
               GROUP BY a.company_id, {cols_with_pre_fix}
            RETURNING id
        """
        )

        env = util.env(cr)
        created_account_group = env["account.group"].browse([i[0] for i in cr.fetchall()])

        # Delete old account group before set parent and set in chart of account(account.account).
        cr.execute(
            """
            DELETE FROM account_group
             WHERE id in %s
        """,
            [
                old_groups_ids,
            ],
        )

        created_account_group._adapt_parent_account_group()
        created_account_group._adapt_accounts_for_account_groups()
