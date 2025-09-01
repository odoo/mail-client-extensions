from odoo.upgrade import util


def _setup_return_type_company_dependent_field(cr, field):
    """
    Similar to 'make_field_company_dependent' but does not require a field company_id as there is none on return types
    """
    if not util.column_exists(cr, "account_return_type", field):
        return

    old_field_new_name = f"default_{field}"
    util.rename_field(cr, "account.return.type", field, old_field_new_name, update_references=False)
    util.create_column(cr, "account_return_type", field, "jsonb")

    query = util.format_query(
        cr,
        """
        WITH _data AS (
             SELECT t.id,
                    jsonb_object_agg(c.id, t.{old_field_new_name}) as j
               FROM account_return_type t,
                    res_company c
           GROUP BY t.id
        )
        UPDATE account_return_type t
           SET {field} = d.j
          FROM _data d
         WHERE d.id = t.id
        """,
        old_field_new_name=old_field_new_name,
        field=field,
    )
    cr.execute(query)


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

        mapping = {"success": "reviewed", "failure": "anomaly", "manual": "todo"}
        util.change_field_selection_values(cr, "account.return.check", "result", mapping)

        util.create_column(cr, "account_return_check", "refresh_result", "bool")
        util.create_m2m(cr, util.AUTO, "account_return_check", "res_users")

        # If the check has been bypassed or approvers were added, we consider that a manual action has been done
        # so refresh_result = False and result = 'reviewed'.
        cr.execute("""
            WITH check_has_approvers AS (
                   SELECT account_return_check.id AS id,
                          BOOL_AND(check_approvers.account_return_check_id IS NOT NULL) AS has_approvers
                     FROM account_return_check
                LEFT JOIN account_return_check_res_users_rel check_approvers
                       ON account_return_check.id = check_approvers.account_return_check_id
                 GROUP BY account_return_check.id
            )
            UPDATE account_return_check
               SET refresh_result = (bypassed OR check_has_approvers.has_approvers) IS NOT TRUE,
                   result = CASE
                                WHEN bypassed OR check_has_approvers.has_approvers THEN 'reviewed'
                                ELSE result
                            END
              FROM check_has_approvers
             WHERE account_return_check.id = check_has_approvers.id
        """)

    util.remove_field(cr, "account.return.check", "notes")
    util.remove_field(cr, "account.return.creation.wizard", "show_warning_existing_return")
    _setup_return_type_company_dependent_field(cr, "deadline_periodicity")
    _setup_return_type_company_dependent_field(cr, "deadline_start_date")

    util.rename_field(cr, "account.return", "amount_to_pay", "total_amount_to_pay")
    util.remove_field(cr, "account.return.type", "report_country_id")

    util.remove_field(cr, "account.return.check", "bypassed")
    util.remove_field(cr, "account.return.check", "show_supervise")
    util.remove_field(cr, "account.return.check", "show_invalidate")
