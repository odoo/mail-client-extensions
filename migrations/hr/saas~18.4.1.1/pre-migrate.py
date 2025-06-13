from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE hr_employee SET gender = NULL WHERE gender = 'other'")
    cr.execute("SELECT 1 FROM ir_module_module WHERE name='base' AND demo")
    if bool(cr.rowcount):
        util.create_column(cr, "hr_employee", "_upg_existing", "bool", default=True)
    util.rename_field(cr, "hr.employee", "gender", "sex")
    util.rename_field(cr, "res.users", "gender", "sex")
    util.create_column(cr, "hr_employee", "current_version_id", "int4")

    if util.table_exists(cr, "hr_contract"):
        cr.execute(
            """
            UPDATE hr_contract
               SET active = False
             WHERE employee_id IS NOT NULL
               AND (
                    state='cancel'
                    OR (state='draft' AND kanban_state != 'done')
                   )
            """
        )
        util.rename_model(cr, "hr.contract", "hr.version")

        cr.execute("UPDATE hr_employee SET current_version_id = contract_id WHERE contract_id IS NOT NULL")
        util.rename_field(cr, "hr.employee", "contract_id", "version_id")

        util.rename_field(cr, "hr.version", "date_start", "contract_date_start")
        util.rename_field(cr, "hr.version", "date_end", "contract_date_end")

        util.create_column(cr, "hr_version", "date_version", "date")
        cr.execute("UPDATE hr_version SET date_version = contract_date_start")

        # job_title is now stored computed, after renaming hr_contract -> hr_version
        # create the column and prefill the values to avoid compute by ORM
        util.create_column(cr, "hr_version", "job_title", "varchar")
        query = """
           WITH _job_title AS (
                SELECT v.id,
                       COALESCE(j.name->>e.lang, j.name->>'en_US') as title
                  FROM hr_version v
                  JOIN hr_job j
                    ON j.id = v.job_id
             LEFT JOIN hr_employee e
                    ON e.id = v.employee_id
                 WHERE {parallel_filter}
           )
            UPDATE hr_version v
               SET job_title = j.title
              FROM _job_title j
             WHERE v.id = j.id
        """
        util.explode_execute(cr, query, table="hr_version", alias="v")

    cr.execute(
        """
            INSERT INTO mail_message(
                model, res_id, record_name, author_id, message_type, body, subtype_id
            )
                 SELECT 'hr.employee',
                        e.id,
                        e.name,
                        %s,
                        'comment',
                        e.notes,
                        %s
                   FROM hr_employee e
                  WHERE e.notes IS NOT NULL
        """,
        [util.ref(cr, "base.partner_root"), util.ref(cr, "mail.mt_note")],
    )

    keep_employee_fields = [
        "active",
        "color",
        "company_id",
        "address_id",
        "mobile_phone",
        "name",
        "resource_id",
        "user_id",
        "share",
        "work_contact_id",
        "work_phone",
        "work_email",
        "department_id",
        "job_id",
        "email",
        "work_location_id",
        "resource_calendar_id",
        "is_flexible",
        "is_fully_flexible",
        "coach_id",
        "parent_id",
        "tz",
        "hr_presence_state",
        "last_activity",
        "last_activity_time",
        "hr_icon_display",
        "show_hr_icon_display",
        "im_status",
        "newly_hired",
        "member_of_department",
    ]

    keep_employee_public_fields = [
        "active",
        "address_id",
        "color",
        "company_id",
        "department_id",
        "job_id",
        "mobile_phone",
        "name",
        "coach_id",
        "parent_id",
        "resource_calendar_id",
        "resource_id",
        "user_id",
        "work_contact_id",
        "work_email",
        "work_location_id",
        "work_phone",
        "tz",
        "last_activity",
        "last_activity_time",
        "hr_icon_display",
        "show_hr_icon_display",
        "member_of_department",
    ]

    if util.module_installed(cr, "hr_homeworking"):
        keep_employee_fields += [
            "monday_location_id",
            "tuesday_location_id",
            "wednesday_location_id",
            "thursday_location_id",
            "friday_location_id",
            "saturday_location_id",
            "sunday_location_id",
            "exceptional_location_id",
            "today_location_name",
        ]
        keep_employee_public_fields += [
            "monday_location_id",
            "tuesday_location_id",
            "wednesday_location_id",
            "thursday_location_id",
            "friday_location_id",
            "saturday_location_id",
            "sunday_location_id",
            "today_location_name",
        ]

    if util.module_installed(cr, "hr_holidays"):
        keep_employee_fields += [
            "leave_manager_id",
            "current_leave_state",
            "leave_date_from",
            "leave_date_to",
            "allocation_count",
            "allocations_count",
            "show_leaves",
            "is_absent",
            "allocation_display",
            "allocation_remaining_display",
        ]
        keep_employee_public_fields += [
            "leave_manager_id",
            "leave_date_to",
            "show_leaves",
            "is_absent",
            "allocation_display",
        ]

    if util.module_installed(cr, "hr_gamification"):
        keep_employee_fields += [
            "goal_ids",
            "badge_ids",
            "direct_badge_ids",
        ]
        keep_employee_public_fields += [
            "badge_ids",
        ]

    if util.module_installed(cr, "hr_presence"):
        keep_employee_fields += [
            "email_sent",
            "hr_presence_state_display",
            "ip_connected",
            "manually_set_presence",
            "manually_set_present",
        ]
        keep_employee_public_fields += [
            "email_sent",
            "hr_presence_state_display",
            "ip_connected",
            "manually_set_presence",
            "manually_set_present",
        ]

    if util.module_installed(cr, "hr_appraisal"):
        keep_employee_fields += [
            "parent_user_id",
            "last_appraisal_id",
            "last_appraisal_state",
        ]
        keep_employee_public_fields += [
            "parent_user_id",
            "last_appraisal_id",
            "last_appraisal_state",
        ]

    if util.module_installed(cr, "hr_expense"):
        keep_employee_fields += [
            "filter_for_expense",
        ]
        keep_employee_public_fields += [
            "filter_for_expense",
        ]

    if util.module_installed(cr, "hr_org_chart"):
        keep_employee_fields += [
            "child_all_count",
            "department_color",
            "child_count",
        ]
        keep_employee_public_fields += [
            "child_all_count",
            "department_color",
            "child_count",
        ]

    if util.module_installed(cr, "sale_timesheet_enterprise"):
        keep_employee_fields += [
            "billable_time_target",
            "show_billable_time_target",
        ]
        keep_employee_public_fields += [
            "billable_time_target",
            "show_billable_time_target",
        ]

    if util.module_installed(cr, "planning"):
        keep_employee_fields += [
            "has_slots",
        ]
        keep_employee_public_fields += [
            "has_slots",
        ]

    util.remove_inherit_from_model(cr, "hr.employee", "hr.employee.base", keep=keep_employee_fields)
    util.remove_inherit_from_model(cr, "hr.employee.public", "hr.employee.base", keep=keep_employee_public_fields)
    util.remove_model(cr, "hr.employee.base")

    util.remove_field(cr, "hr.employee", "sinid")
    util.remove_field(cr, "hr.employee", "vehicle")
    util.remove_field(cr, "hr.employee", "first_contract_date")
    util.remove_field(cr, "hr.employee", "contract_warning")
    util.remove_field(cr, "hr.employee", "calendar_mismatch")
    util.remove_field(cr, "hr.employee", "contracts_count")
    util.remove_field(cr, "hr.employee", "notes")

    util.remove_field(cr, "hr.employee.public", "first_contract_date")

    util.remove_field(cr, "hr.version", "first_contract_date")
    util.remove_field(cr, "hr.version", "calendar_mismatch")
    util.remove_field(cr, "hr.version", "visa_no")
    util.remove_field(cr, "hr.version", "permit_no")
    util.remove_field(cr, "hr.version", "state")
    util.remove_field(cr, "hr.version", "kanban_state")
    util.remove_field(cr, "hr.version", "contracts_count")
    util.remove_field(cr, "hr.version", "notes")
    util.rename_field(cr, "hr.version", "default_contract_id", "contract_template_id")

    util.remove_model(cr, "hr.contract.history")
    util.remove_model(cr, "hr.contract.employee.report")

    util.rename_field(cr, "hr.employee", "contract_ids", "version_ids")

    util.remove_field(cr, "resource.calendar", "contract_ids")
    util.remove_field(cr, "resource.calendar", "running_contracts_count")
    util.remove_field(cr, "resource.calendar", "contracts_count")

    util.remove_field(cr, "res.users", "vehicle")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr.contract_type_{part_time,intern}"))
    util.remove_record(cr, "hr.ir_cron_data_check_work_permit_validity")

    util.remove_view(cr, "hr.resource_calendar_view_form")
    util.remove_view(cr, "hr.view_resource_calendar_search_inherit_contract")
    util.remove_view(cr, "hr.resource_calendar_view_tree")
    util.remove_view(cr, "hr.view_employee_public_form")
    util.remove_view(cr, "hr.hr_employee_view_pivot_inherit_hr_contract")
    util.remove_view(cr, "hr.hr_employee_view_graph_inherit_hr_contract")
    util.remove_view(cr, "hr.hr_contract_employee_list_inherit")
    util.remove_view(cr, "hr.hr_user_view_form")
    util.remove_view(cr, "hr.hr_employee_view_search")
    util.remove_view(cr, "hr.hr_hr_employee_view_form3")
    util.remove_view(cr, "hr.hr_hr_employee_view_form2")
    util.remove_view(cr, "hr.hr_contract_view_tree_contract_templates")
    util.remove_view(cr, "hr.hr_contract_view_form_contract_templates")
    util.remove_view(cr, "hr.hr_contract_view_activity")
    util.remove_view(cr, "hr.hr_contract_view_kanban")
    util.remove_view(cr, "hr.hr_contract_view_tree")
    util.remove_view(cr, "hr.hr_contract_view_form")
    util.remove_view(cr, "hr.hr_contract_view_search")
    util.remove_menus(cr, [util.ref(cr, "hr.menu_hr_reporting_timesheet")])
