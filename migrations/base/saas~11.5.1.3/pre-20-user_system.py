# -*- coding: utf-8 -*-
import os
from ast import literal_eval
from collections import defaultdict

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    def try_id_2(table):
        cr.execute("SELECT count(1) FROM {} WHERE id=2".format(table))
        [has] = cr.fetchone()
        if has:
            cr.execute("SELECT nextval('{}_id_seq')".format(table))
            return cr.fetchone()[0]
        return 2

    u1id = 1
    u2id = util.ENVIRON["user2_id"] = try_id_2("res_users")

    cr.execute("SELECT partner_id FROM res_users WHERE id=1")
    p1id = cr.fetchone()[0]
    p2id = try_id_2("res_partner")

    # copy partner
    cols = ", ".join(util.get_columns(cr, "res_partner")[0])
    query = """
        INSERT INTO res_partner(id, {0})
             SELECT %s, {0}
               FROM res_partner
              WHERE id = %s
    """
    cr.execute(query.format(cols), [p2id, p1id])

    # and user (but keep same partner)
    # by keeping same partner we do not need to reassign every fk...
    cols = ", ".join(util.get_columns(cr, "res_users", ignore=("id", "login", "oauth_uid"))[0])
    query = """
        INSERT INTO res_users(id, login, {0})
          SELECT %s, CONCAT('\a', login), {0}
            FROM res_users
           WHERE id = %s
    """
    cr.execute(query.format(cols), [u2id, u1id])

    # now reassign partner2 to user1
    cr.execute("UPDATE res_users SET partner_id=%s WHERE id=%s", [p2id, u1id])

    # and track them
    cr.execute("UPDATE ir_model_data SET res_id=%s WHERE module='base' AND name='partner_root'", [p2id])
    query = """
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             VALUES
                ('base', 'partner_admin', 'res.partner', %s, true),
                ('base', 'user_admin', 'res.users', %s, true)
        ON CONFLICT (module, name)
        DO UPDATE SET noupdate = true, res_id = excluded.res_id
    """
    cr.execute(
        """
        ALTER TABLE ir_model_data
        ADD CONSTRAINT ir_model_data_module_name_uniq_constraint_for_conflict
        unique(module,name)
    """
    )
    cr.execute(query, [p1id, u2id])
    cr.execute(
        """
    ALTER TABLE ir_model_data
    DROP CONSTRAINT ir_model_data_module_name_uniq_constraint_for_conflict
    """
    )

    # rename and deactivate user1 and partner2, reset password
    query = """
        UPDATE res_partner
           SET name='System',
               company_id = NULL,
               active = false
         WHERE id = %s
    """
    cr.execute(query, [p2id])

    query = """
        UPDATE res_users
           SET login='__system__',
               password=NULL,
               active=false,
               signature='<span>--<br/>System</span>'
         WHERE id = %s
    """
    cr.execute(query, [u1id])
    cr.execute("UPDATE res_users SET login=substring(login, 2) WHERE id=%s", [u2id])

    # move oauth_uid from user 1 to user 2
    if util.column_exists(cr, "res_users", "oauth_uid"):
        cr.execute("SELECT oauth_uid FROM res_users WHERE id=%s", [u1id])
        oauth_uid = cr.fetchone()[0]
        if oauth_uid:
            cr.execute("UPDATE res_users SET oauth_uid = NULL WHERE id=%s", [u1id])
            cr.execute("UPDATE res_users SET oauth_uid = %s WHERE id=%s", [oauth_uid, u2id])

    # copy groups
    cr.execute(
        """
        INSERT INTO res_groups_users_rel(gid, uid)
             SELECT gid, %s
               FROM res_groups_users_rel
              WHERE uid = %s
    """,
        [u2id, u1id],
    )

    # copy companies
    cr.execute(
        """
        INSERT INTO res_company_users_rel(cid, user_id)
             SELECT cid, %s
               FROM res_company_users_rel
              WHERE user_id = %s
    """,
        [u2id, u1id],
    )

    # reassign everything to user 2 except some fields that should be kept linked to __system__
    ignored = [
        ("res_groups_users_rel", "uid"),  # already copied above
        ("res_company_users_rel", "user_id"),  # already copied above
        ("ir_cron", "user_id"),
        ("mail_activity", "create_user_id"),  # second create_uid (wtf?)
        ("mail_alias", "alias_user_id"),
        ("res_company", "intercompany_user_id"),  # always SUPERUSER (uid=1)
    ]
    if os.environ.get("ODOO_MIG_USER_SYSTEM_IGNORES"):
        ignored += literal_eval(os.environ["ODOO_MIG_USER_SYSTEM_IGNORES"])

    # inhertied tables (and parents) should be processed sequentially
    cr.execute(
        """
        SELECT DISTINCT c.relname
          FROM pg_class c
          JOIN pg_inherits i ON (i.inhrelid = c.oid OR i.inhparent = c.oid)
        """
    )
    tables_with_inheritance = {t for t, in cr.fetchall()}

    def get_queries(table, columns, filter_modules, sequential):
        if not columns:
            return []
        query = "UPDATE {} t SET {} WHERE {}\n{}".format(
            table,
            ",\n".join(
                "{col}=CASE WHEN {col}=%(u1id)s THEN %(u2id)s ELSE {col} END".format(col=col) for col in columns
            ),
            "({})".format(" OR ".join("{}=%(u1id)s".format(col) for col in columns)),
            """
            AND NOT EXISTS
            (
                SELECT 1
                FROM ir_model_data d
                WHERE d.model = %(model)s
                    AND COALESCE(d.module, '') NOT IN ('', '__export__')
                    AND t.id=d.res_id
            )
            """
            if filter_modules
            else "",
        )
        query = cr.mogrify(query, {"u1id": u1id, "u2id": u2id, "model": util.model_of_table(cr, table)}).decode()
        if sequential or not util.column_exists(cr, table, "id"):
            return [query]
        return util.explode_query_range(cr, query, table, alias="t")

    table_cols = defaultdict(set)
    for table, fk, _, _ in util.get_fk(cr, "res_users"):
        if table == "ir_model_data":
            continue
        if (table, fk) in ignored:
            continue
        table_cols[table].add(fk)

    sequential_queries = []
    uid_queries = []
    other_queries = []
    for table, cols in table_cols.items():
        uid_cols = cols & {"create_uid", "write_uid"}
        other_cols = cols - {"create_uid", "write_uid"}
        if table in tables_with_inheritance:
            sequential_queries.extend(get_queries(table, uid_cols, True, sequential=True))
            sequential_queries.extend(get_queries(table, other_cols, False, sequential=True))
        else:
            uid_queries.extend(get_queries(table, uid_cols, True, sequential=False))
            other_queries.extend(get_queries(table, other_cols, False, sequential=False))

    util._logger.info("Running %s sequential queries", len(sequential_queries))
    for query in sequential_queries:
        cr.execute(query)
    util._logger.info("Running create/write uid queries")
    util.parallel_execute(cr, uid_queries)
    util._logger.info("Running other queries")
    util.parallel_execute(cr, other_queries)
