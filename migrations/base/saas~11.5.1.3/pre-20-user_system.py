# -*- coding: utf-8 -*-
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
    ]

    for table, fk, _, _ in util.get_fk(cr, "res_users"):
        if fk in ("create_uid", "write_uid"):
            continue
        if (table, fk) in ignored:
            continue
        query = """
            UPDATE {table}
               SET {fk} = %s
             WHERE {fk} = %s
        """
        cr.execute(query.format(table=table, fk=fk), [u2id, u1id])
