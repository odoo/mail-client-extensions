from odoo.upgrade import util


def migrate(cr, version):
    # missing columns removals from saas~13.5 (see odoo/upgrade@a25ddc9de)
    util.remove_column(cr, "hr_leave", "name")
    util.remove_column(cr, "hr_leave_allocation", "name")

    cr.execute("""
        ALTER TABLE hr_leave_allocation
      RENAME COLUMN private_name
                 TO name
    """)
    util.update_field_usage(cr, "hr.leave.allocation", "private_name", "name")
    util.remove_field(cr, "hr.leave.allocation", "private_name")

    util.change_field_selection_values(
        cr,
        "hr.leave.type",
        "allocation_validation_type",
        {
            "officer": "hr",
            "no": "no_validation",
        },
    )

    cr.execute(
        "DELETE FROM hr_leave WHERE holiday_type in ('company', 'department', 'category') OR employee_id IS NULL"
    )
    cr.execute(
        "DELETE FROM hr_leave_allocation WHERE holiday_type in ('company', 'department', 'category') OR employee_id IS NULL"
    )

    util.remove_constraint(cr, "hr_leave", "hr_leave_type_value")
    util.remove_constraint(cr, "hr_leave_allocation", "hr_leave_allocation_type_value")

    util.remove_field(cr, "hr.leave", "parent_id")
    util.remove_field(cr, "hr.leave", "linked_request_ids")
    util.remove_field(cr, "hr.leave", "holiday_type")
    util.remove_field(cr, "hr.leave", "employee_ids")
    util.remove_field(cr, "hr.leave", "multi_employee")
    util.remove_field(cr, "hr.leave", "category_id")
    util.remove_field(cr, "hr.leave", "mode_company_id")
    util.remove_field(cr, "hr.leave", "all_employee_ids")

    util.remove_field(cr, "hr.leave.allocation", "parent_id")
    util.remove_field(cr, "hr.leave.allocation", "linked_request_ids")
    util.remove_field(cr, "hr.leave.allocation", "holiday_type")
    util.remove_field(cr, "hr.leave.allocation", "employee_ids")
    util.remove_field(cr, "hr.leave.allocation", "multi_employee")
    util.remove_field(cr, "hr.leave.allocation", "mode_company_id")
    util.remove_field(cr, "hr.leave.allocation", "category_id")
    util.remove_field(cr, "hr.leave.allocation", "has_accrual_plan")

    util.remove_field(cr, "hr.leave.report", "holiday_type")
    util.remove_field(cr, "hr.leave.report", "category_id")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_holidays.{act_hr_employee_holiday_type,action_hr_leave_report}"))
