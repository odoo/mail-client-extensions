# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_holidays.menu_hr_holidays_{approvals,management}"))
    util.rename_model(cr, "hr.leave.stress.day", "hr.leave.mandatory.day")
    util.rename_field(cr, "hr.leave", "has_stress_day", "has_mandatory_day")

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
