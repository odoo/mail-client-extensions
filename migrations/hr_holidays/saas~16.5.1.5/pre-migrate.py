import itertools

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_holidays.menu_hr_holidays_{approvals,management}"))
    util.rename_model(cr, "hr.leave.stress.day", "hr.leave.mandatory.day")
    util.rename_field(cr, "hr.leave", "has_stress_day", "has_mandatory_day")
    util.remove_field(cr, "hr.leave", "holiday_allocation_id")
    util.remove_field(cr, "hr.leave.type", "closest_allocation_to_expire")
    util.remove_field(cr, "hr.leave.type", "virtual_leaves_taken")
    util.remove_field(cr, "hr.leave.type", "remaining_leaves")
    util.remove_field(cr, "hr.leave.allocation", "taken_leave_ids")
    util.remove_field(cr, "hr.leave.allocation", "can_reset")

    rename_records = [
        "hr_holidays.hr_leave_stress_day_view_search",
        "hr_holidays.hr_leave_stress_day_view_list",
        "hr_holidays.hr_leave_stress_day_view_form",
        "hr_holidays.hr_leave_stress_day_rule_multi_company",
        "hr_holidays.hr_leave_stress_day_action",
        "hr_holidays.hr_leave_stress_day_1",
        "hr_holidays.hr_holidays_stress_day_menu_configuration",
        "hr_holidays.access_hr_leave_stress_day_manager",
        "hr_holidays.access_hr_leave_stress_day_user",
    ]

    for record in rename_records:
        util.rename_xmlid(cr, record, record.replace("stress", "mandatory"))

    cr.execute("DELETE FROM hr_leave_allocation WHERE state IN ('draft', 'cancel')")
    amount_deleted = cr.rowcount

    # warn admins
    if amount_deleted:
        util.add_to_migration_reports(
            f"""
<details>
<summary>
    Due to the removal of Draft and Cancel states on the time off allocations,
    every allocation that was in one of those states prior to the migration to 17.0
    has been removed.
    On your database, a total of {amount_deleted} allocation(s) were removed.
    If you allow employees to make allocation requests, it might be advised to
    communicate this information so that they can create a new one if needed.
</summary>
</details>
            """,
            category="Time Off",
            format="html",
        )

    util.change_field_selection_values(
        cr,
        "hr.leave.accrual.level",
        "added_value_type",
        {
            "days": "day",
            "hours": "hour",
        },
    )
    util.change_field_selection_values(
        cr, "hr.leave.accrual.level", "action_with_unused_accruals", {"postponed": "all"}
    )
    util.remove_field(cr, "hr.leave.accrual.level", "parent_id")
    util.remove_column(cr, "hr_leave_accrual_level", "parent_path")  # if parent_store was set by any inheriting module.

    util.create_column(cr, "hr_leave_accrual_plan", "is_based_on_worked_time", "boolean", default=False)
    cr.execute(
        """
            WITH plans AS (
          SELECT accrual_plan_id
            FROM hr_leave_accrual_level
           WHERE is_based_on_worked_time = true
        GROUP BY accrual_plan_id
            )
            UPDATE hr_leave_accrual_plan p
               SET is_based_on_worked_time = true
              FROM plans o
             WHERE o.accrual_plan_id = p.id
        """
    )

    cr.execute(
        """
            UPDATE hr_leave_accrual_level l
               SET added_value_type = CASE WHEN t.request_unit in ('day', 'half_day') THEN 'day' ELSE 'hour' END
              FROM hr_leave_accrual_plan p
              JOIN hr_leave_type t
                ON t.id = p.time_off_type_id
             WHERE p.id = l.accrual_plan_id
        """
    )
    cr.execute(
        """
            WITH plan_no_type AS (
                SELECT p.id,
                       (array_agg(l.added_value_type ORDER BY l.sequence ASC))[1] as avt
                  FROM hr_leave_accrual_level l
                  JOIN hr_leave_accrual_plan p
                    ON p.id = l.accrual_plan_id
                 WHERE p.time_off_type_id IS NULL
              GROUP BY p.id
            )
            UPDATE hr_leave_accrual_level l
               SET added_value_type = p.avt
              FROM plan_no_type p
             WHERE p.id = l.accrual_plan_id
        """
    )

    util.create_column(cr, "hr_leave_accrual_plan", "added_value_type", "varchar")
    cr.execute(
        """
            WITH plans AS (
                SELECT p.id,
                       (array_agg(l.added_value_type ORDER BY l.sequence ASC))[1] as avt
                  FROM hr_leave_accrual_level l
                  JOIN hr_leave_accrual_plan p
                    ON p.id = l.accrual_plan_id
              GROUP BY p.id
            )
            UPDATE hr_leave_accrual_plan p
               SET added_value_type = o.avt
              FROM plans o
             WHERE p.id = o.id
        """
    )

    util.remove_field(cr, "hr.leave.accrual.level", "is_based_on_worked_time")

    util.create_column(cr, "hr_leave", "company_id", "int4", fk_table="res_company", on_delete_action="SET NULL")

    company_id_queries = [
        """
        UPDATE hr_leave l
           SET company_id = employee_company_id
         WHERE employee_company_id IS NOT NULL
           AND holiday_type != 'department'
        """,
        """
        UPDATE hr_leave l
           SET company_id = mode_company_id
         WHERE mode_company_id IS NOT NULL
           AND employee_company_id IS NULL
           AND holiday_type != 'department'
        """,
        """
        UPDATE hr_leave l
           SET company_id = d.company_id
          FROM hr_department d
         WHERE d.id = l.department_id
           AND l.holiday_type = 'department'
        """,
    ]
    util.parallel_execute(
        cr,
        list(
            itertools.chain.from_iterable(
                (util.explode_query_range(cr, query, table="hr_leave", alias="l") for query in company_id_queries)
            )
        ),
    )

    util.create_column(
        cr, "hr_leave", "resource_calendar_id", "int4", fk_table="resource_calendar", on_delete_action="SET NULL"
    )
    util.create_column(cr, "hr_leave", "number_of_hours", "int4", default=0)

    queries = [
        """
        UPDATE hr_leave l
           SET resource_calendar_id = e.resource_calendar_id
          FROM hr_employee e
         WHERE e.id = l.employee_id
           AND l.holiday_type = 'employee'
           AND l.resource_calendar_id IS NULL
        """,
        """
        UPDATE hr_leave l
           SET resource_calendar_id = c.resource_calendar_id
          FROM res_company c
         WHERE c.id = l.mode_company_id
           AND l.holiday_type = 'company'
           AND l.resource_calendar_id IS NULL
        """,
        """
        UPDATE hr_leave l
           SET resource_calendar_id = c.resource_calendar_id
          FROM hr_department d
          JOIN res_company c
            ON d.company_id = c.id
         WHERE d.id = l.department_id
           AND l.holiday_type = 'department'
           AND l.resource_calendar_id IS NULL
        """,
    ]
    util.parallel_execute(
        cr,
        list(
            itertools.chain.from_iterable(
                (util.explode_query_range(cr, query, table="hr_leave", alias="l") for query in queries)
            )
        ),
    )
    util.remove_field(cr, "hr.leave.report", "active")
    util.remove_field(cr, "hr.leave.report", "allocation_id")
    util.remove_field(cr, "hr.leave.report", "active_employee")
    util.remove_view(cr, "hr_holidays.hr_leave_report_view_form")
    util.remove_record(cr, "hr_holidays.act_hr_employee_holiday_request")

    util.if_unchanged(cr, "hr_holidays.mail_act_leave_approval", util.update_record_from_xml)
