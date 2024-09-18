from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        WITH approvers AS (
            INSERT INTO studio_approval_rule_approver (rule_id, create_uid, user_id)
                SELECT id, COALESCE(create_uid,%(admin)s), COALESCE(create_uid,%(admin)s)
                FROM studio_approval_rule
                UNION
                SELECT id, COALESCE(create_uid,%(admin)s), responsible_id
                FROM studio_approval_rule
                WHERE responsible_id is not NULL
            RETURNING rule_id, user_id
        )
        INSERT INTO approval_rule_users_to_notify_rel (studio_approval_rule_id, res_users_id)
               SELECT rule_id, user_id FROM approvers
               ON CONFLICT DO NOTHING
    """,
        {"admin": util.ref(cr, "base.user_admin")},
    )

    util.remove_field(cr, "studio.approval.rule", "responsible_id")
