from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave", "manager_id")
    util.remove_view(cr, "hr_holidays.hr_employee_public_form_view_inherit")

    util.create_column(cr, "hr_leave_accrual_plan", "can_be_carryover", "boolean", default=True)
    util.create_column(cr, "hr_leave_accrual_level", "carryover_options", "varchar")
    util.create_column(cr, "hr_leave_accrual_level", "milestone_date", "varchar")

    cr.execute(
        """
        UPDATE hr_leave_accrual_level
            SET carryover_options = CASE
                    WHEN action_with_unused_accruals = 'maximum' THEN 'limited'
                    ELSE 'unlimited'
                END,
                milestone_date = CASE
                    WHEN start_count > 0 THEN 'after'
                    ELSE 'creation'
                END;
        """
    )

    util.change_field_selection_values(cr, "hr.leave.accrual.level", "action_with_unused_accruals", {"maximum": "all"})
