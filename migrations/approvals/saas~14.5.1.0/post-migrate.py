# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO approval_category_approver(category_id, user_id)
        SELECT approval_category_id as category_id,
            res_users_id as user_id
        FROM approval_category_res_users_rel
        """
    )
    cr.execute("DROP TABLE approval_category_res_users_rel")
