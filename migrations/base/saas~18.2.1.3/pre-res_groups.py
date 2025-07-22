from odoo.upgrade import util


def migrate(cr, version):
    # update domain values
    for df in util.domains._get_domain_fields(cr):
        cr.execute(
            util.format_query(
                cr,
                """
                UPDATE {table}
                   SET {column}= REPLACE(
                           {column},
                           '[g.id for g in user.groups_id]',
                           'user.all_group_ids.ids'
                        )
                  WHERE {column} LIKE '%[g.id for g in user.groups_id]%'
                """,
                table=df.table,
                column=df.domain_column,
            )
        )
        cr.execute(
            util.format_query(
                cr,
                """
                UPDATE {table}
                   SET {column}= REPLACE(
                           {column},
                           'user.groups_id.ids',
                           'user.all_group_ids.ids'
                        )
                WHERE {column} LIKE '%user.groups_id.ids%'
                """,
                table=df.table,
                column=df.domain_column,
            )
        )

    def gen_adapter(old, new):
        def adapter(leaf, _or, _neg):
            left, op, right = leaf
            path = left.split(".")
            if path[-2:] == [old, "id"] and op in ("=", "!="):
                op = "in" if op == "=" else "not in"
                path[-2:] = [new]
                right = [right]
            path = [new if part == old else part for part in path]
            leaf = (".".join(path), op, right)
            return [leaf]

        return adapter

    # Additions are always made on `user_ids`.
    # For domains it is the computed field `all_user_ids` (users having this
    # group or being inside from implied groups).
    util.rename_field(cr, "res.groups", "users", "user_ids", domain_adapter=gen_adapter("users", "all_user_ids"))
    util.rename_field(cr, "res.groups", "trans_implied_ids", "all_implied_ids")

    # Additions are always made on `group_ids`.
    # For domains it is the computed field `all_group_ids`.
    util.rename_field(
        cr, "res.users", "groups_id", "group_ids", domain_adapter=gen_adapter("groups_id", "all_group_ids")
    )

    # The fields below do not have an all_group_ids variant. There are no cases
    # where implied groups are used by these models.
    util.rename_field(cr, "ir.actions.act_window", "groups_id", "group_ids")
    util.rename_field(cr, "ir.actions.server", "groups_id", "group_ids")
    util.rename_field(cr, "ir.actions.report", "groups_id", "group_ids")
    util.rename_field(cr, "ir.ui.view", "groups_id", "group_ids")
    util.rename_field(cr, "ir.ui.menu", "groups_id", "group_ids")
    util.rename_field(cr, "ir.cron", "groups_id", "group_ids")

    # remove dynamic fields and related view
    util.remove_view(cr, "base.user_groups_view")
    util.remove_field(cr, "res.users", "user_group_warning")

    # Remove users from implied groups, now handled by computed m2m
    cr.execute(
        """
        WITH RECURSIVE all_implied AS (
            SELECT users.uid,
                   implied.hid
              FROM res_groups_users_rel users
              JOIN res_groups_implied_rel implied
                ON users.gid = implied.gid
             UNION
            SELECT result.uid,
                   implied.hid
              FROM res_groups_implied_rel implied
              JOIN all_implied result
                ON implied.gid = result.hid
        )
        DELETE FROM res_groups_users_rel users
         USING all_implied result
         WHERE users.uid = result.uid
           AND users.gid = result.hid
        """
    )
