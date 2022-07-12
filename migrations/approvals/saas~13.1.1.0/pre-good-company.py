# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "approval_category", "company_id", "integer")
    util.create_column(cr, "approval_category", "_tmp", "integer")

    columns = util.get_columns(cr, "approval_category", ignore=("id", "_tmp", "company_id"))
    columns_ac = [f"ac.{c}" for c in columns]

    # duplicate categories
    cr.execute(
        """
        WITH companies AS (
            SELECT array_agg(id ORDER BY id) as cids FROM res_company
        ),
        _upd AS (
            UPDATE approval_category ac
               SET company_id = cc.cids[1], _tmp = ac.id
              FROM companies cc
             WHERE ac.company_id IS NULL
        )
        INSERT INTO approval_category(_tmp, company_id, {})
             SELECT ac.id, unnest(cc.cids[1:]), {}
               FROM approval_category ac,
                    companies cc
              WHERE ac.company_id IS NULL
    """.format(
            ",".join(columns), ",".join(columns_ac)
        )
    )

    # copy & clean m2m to users
    cr.execute(
        """
        INSERT INTO approval_category_res_users_rel(approval_category_id, res_users_id)
             SELECT c.id, r.res_users_id
               FROM approval_category_res_users_rel r
               JOIN approval_category c ON c._tmp = r.approval_category_id
              WHERE c.id != c._tmp
    """
    )
    cr.execute(
        """
        DELETE FROM approval_category_res_users_rel r
              USING approval_category c
              WHERE c.id = r.approval_category_id
                AND NOT EXISTS(SELECT 1
                                 FROM res_company_users_rel u
                                WHERE u.user_id = r.res_users_id
                                  AND u.cid = c.company_id)
    """
    )

    cr.execute(
        """
        UPDATE approval_request req
           SET category_id = cat.id
          FROM approval_category cat,
               hr_employee emp
         WHERE cat._tmp = req.category_id
           AND emp.user_id = req.request_owner_id
           AND emp.company_id = cat.company_id
    """
    )

    # XXX `related=..., stored=True` are actually not stored...

    # util.create_column(cr, "approval_request", "company_id", "integer")
    # cr.execute(
    #     """
    #     UPDATE approval_request r
    #        SET company_id = c.company_id
    #       FROM approval_category c
    #      WHERE c.id = r.category_id
    # """
    # )

    # util.create_column(cr, "approval_approver", "company_id", "integer")
    # cr.execute(
    #     """
    #     UPDATE approval_approver a
    #        SET company_id = r.company_id
    #       FROM approval_request r
    #      WHERE r.id = a.request_id
    # """
    # )
