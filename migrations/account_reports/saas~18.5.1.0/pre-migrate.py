from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "account_reports.action_open_view_account_return")

    util.remove_inherit_from_model(cr, "account.return.check", "mail.thread")
    util.remove_inherit_from_model(cr, "account.return.check", "mail.activity.mixin")

    util.remove_view(cr, "account_reports.view_attachment_kanban_inherit_return")
    util.remove_view(cr, "account_reports.account_return_check_list_view")
    util.remove_view(cr, "account_reports.account_return_check_form_view")

    # Account Return model was introduced in 18.3
    if util.table_exists(cr, "account_return"):
        util.create_column(cr, "account_return", "date_lock", "date")
        cr.execute(
            """
            UPDATE account_return
               SET date_lock = date_submission
             WHERE date_submission IS NOT NULL
               AND amount_to_pay IS NOT NULL
            """
        )

    # Removes approver_ids and dispatch values in new fields approver_id and supervisor_id

    # | Scenario                | `approver_id` outcome | `supervisor_id` outcome |
    # | ----------------------- | --------------------- | ----------------------- |
    # | Admin(s) exist          | Set to admin          | Set to admin            |
    # | Only non-admins exist   | Set to any approver   | Remains NULL            |
    # | No approver_ids at all  | Not updated           | Not updated             |

    # Return check model was introduced in 18.3
    if not util.table_exists(cr, "account_return_check"):
        return

    util.create_column(cr, "account_return_check", "approver_id", "int4")
    util.create_column(cr, "account_return_check", "supervisor_id", "int4")
    cr.execute(
        """
            WITH check_admin_candidates AS (
                SELECT return_check.id as return_check_id,
                       MIN(checks_users.res_users_id) FILTER (WHERE admin.id IS NOT NULL) AS admin_user,
                       MIN(checks_users.res_users_id) AS any_user
                  FROM account_return_check return_check
                  JOIN account_return_check_res_users_rel checks_users
                    ON return_check.id = checks_users.account_return_check_id
                  JOIN res_groups_users_rel r
                    ON r.uid = checks_users.res_users_id
             LEFT JOIN ir_model_data admin
                    ON admin.res_id = r.gid
                   AND admin.model = 'res.groups'
                   AND admin.module = 'account'
                   AND admin.name = 'group_account_manager'
                 WHERE return_check.bypassed = TRUE
              GROUP BY return_check.id
            )
            UPDATE account_return_check return_check
               SET approver_id = COALESCE(candidates.admin_user, candidates.any_user),
                   supervisor_id = candidates.admin_user
              FROM check_admin_candidates candidates
             WHERE candidates.return_check_id = return_check.id
        """
    )
    util.remove_field(cr, "account.return.check", "approver_ids")
