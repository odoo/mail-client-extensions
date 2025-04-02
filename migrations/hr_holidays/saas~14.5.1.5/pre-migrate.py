from odoo.upgrade import util


def migrate(cr, version):
    # Columns Creation
    util.create_column(cr, "hr_leave", "holiday_allocation_id", "int4")
    util.create_column(cr, "hr_leave", "multi_employee", "bool", default=False)
    util.create_m2m(cr, "hr_employee_hr_leave_rel", "hr_leave", "hr_employee")
    util.create_column(cr, "hr_leave", "lastcall", "date")
    util.create_column(cr, "hr_leave_type", "color", "int4")
    util.create_column(cr, "hr_leave_type", "icon_id", "int4")
    util.create_column(cr, "hr_leave_type", "requires_allocation", "varchar", default="yes")
    util.create_column(cr, "hr_leave_type", "employee_requests", "varchar", default="no")
    util.create_column(cr, "hr_leave_allocation", "approver_id", "int4")
    util.create_column(cr, "hr_leave_allocation", "multi_employee", "bool")
    util.create_column(cr, "hr_leave_allocation", "accrual_plan_id", "int4")
    util.create_m2m(cr, "hr_employee_hr_leave_allocation_rel", "hr_leave_allocation", "hr_employee")

    # Populate hr_employee_hr_leave_rel for existing leaves
    cr.execute(
        """
            INSERT INTO hr_employee_hr_leave_rel
                 SELECT id, employee_id
                   FROM hr_leave
                  WHERE employee_id IS NOT NULL
        """
    )

    # Populate hr_employee_hr_leave_allocation_rel for existing allocations
    cr.execute(
        """
            INSERT INTO hr_employee_hr_leave_allocation_rel
                 SELECT id, employee_id
                   FROM hr_leave_allocation
                  WHERE employee_id IS NOT NULL
        """
    )

    # Remove cancel state from leaves
    util.change_field_selection_values(cr, "hr.leave", "state", {"cancel": "refuse"})

    # Remove validate1 state from allocations
    util.change_field_selection_values(cr, "hr.leave.allocation", "state", {"validate1": "validate"})

    # This one looks stupid, I know. But when you update twice the same record within a
    # transaction, the second update is slower than the previous one because PG checks for
    # constraints (foreign keys, ...)
    cr.commit()

    # Remove first and second approver id from allocation and set approver_id
    cr.execute(
        """
            UPDATE hr_leave_allocation
            SET approver_id = COALESCE(second_approver_id, first_approver_id)
        """
    )

    # Update allocation_validation_type
    # Set requires_allocation value
    # Set employee_requests value
    queries = [
        """
    UPDATE hr_leave_type
       SET employee_requests='no',
           requires_allocation='yes',
           allocation_validation_type='set'
     WHERE allocation_type='fixed'
       """,
        """
     UPDATE hr_leave_type
        SET employee_requests='yes',
            requires_allocation='no',
            allocation_validation_type='officer'
      WHERE allocation_type='no'
      """,
        """
     UPDATE hr_leave_type
        SET employee_requests='yes',
            requires_allocation='yes',
            allocation_validation_type='officer'
      WHERE allocation_type='fixed_allocation'
      """,
        """
     UPDATE hr_leave_type
        SET employee_requests='no',
            requires_allocation='yes',
            allocation_validation_type='officer'
      WHERE allocation_type NOT IN ('fixed', 'no', 'fixed_allocation')
      """,
    ]
    util.parallel_execute(cr, queries)

    # The way to use accruals in Odoo changed and to avoid problems,
    # we're setting the allocations of type accrual to regular
    # and logging the change so the user knows what he needs to
    # recreate
    cr.execute(
        """
            SELECT id,private_name,employee_id,accrual_limit,number_per_interval,interval_number,unit_per_interval,interval_unit
              FROM hr_leave_allocation
             WHERE allocation_type = 'accrual'
        """
    )
    if cr.rowcount:
        msg = """Due to the migration to the new system of accruals,
        the previous accrual allocations have been converted into regular allocations.
        Your employees have been granted the corresponding amount of hours.
        Please be aware that the previous accruals are no longer valid, you have to create new plans,
        link new allocations to those plans and assign them to your employees in order to be effective.
            %s
        """ % ",".join(
            [
                "hr_leave_allocation: %s, "
                "name: %s, "
                "employee_id :%s, "
                "accrual_limit: %s, "
                "number_per_interval: %s, "
                "interval_number: %s, "
                "unit_per_interval: %s, "
                "interval_unit: %s"
                % (
                    r["id"],
                    r["private_name"],
                    r["employee_id"],
                    r["accrual_limit"],
                    r["number_per_interval"],
                    r["interval_number"],
                    r["unit_per_interval"],
                    r["interval_unit"],
                )
                for r in cr.dictfetchall()
            ]
        )
        util.add_to_migration_reports(msg)

    cr.execute(
        """
            UPDATE hr_leave_allocation
            SET allocation_type = 'regular'
            WHERE allocation_type != 'regular'
        """
    )

    # Migration of validity
    # select id, validity_start, validity_stop from hr_leave_type then set them on hr_leave_allocation where holiday_status_id = id
    # since validity_start was not required and date_from is, we insert an old date in that case.
    cr.execute(
        """
            UPDATE hr_leave_allocation
               SET date_from = COALESCE(type.validity_start, hr_leave_allocation.date_from, '1970-01-01'),
                   date_to = COALESCE(type.validity_stop, hr_leave_allocation.date_to)
              FROM hr_leave_type AS type
             WHERE type.id = hr_leave_allocation.holiday_status_id
        """
    )

    # Migration of holiday_allocation_id
    cr.execute(
        """
        UPDATE hr_leave leave
           SET holiday_allocation_id=allocation.id
          FROM hr_leave_allocation allocation
          JOIN hr_leave_type leave_type
            ON leave_type.id=allocation.holiday_status_id
         WHERE leave.date_from IS NOT NULL AND leave.date_to IS NOT NULL
           AND leave.employee_id = allocation.employee_id
           AND allocation.state = 'validate'
           AND allocation.holiday_status_id=leave.holiday_status_id
           AND leave_type.requires_allocation = 'yes'
           AND allocation.date_from <= leave.date_from
           AND (allocation.date_to IS NULL OR allocation.date_to >= leave.date_to)
    """
    )

    # Some leaves may be missing an allocation due to an invalid operation on the hr officer's part.
    # First pass similar to the first query to populate holiday_allocation_id but this time with more permissive date checks.
    cr.execute(
        """
        UPDATE hr_leave leave
           SET holiday_allocation_id=allocation.id
          FROM hr_leave_allocation allocation
          JOIN hr_leave_type leave_type
            ON leave_type.id=allocation.holiday_status_id
         WHERE leave.holiday_allocation_id IS NULL
           AND leave.employee_id = allocation.employee_id
           AND allocation.state = 'validate'
           AND allocation.holiday_status_id = leave.holiday_status_id
           AND leave_type.requires_allocation = 'yes'
           AND allocation.date_from <= (date_trunc('year', leave.date_from) + INTERVAL '1 year' - INTERVAL '1 day')
           AND (allocation.date_to IS NULL OR allocation.date_to >= date_trunc('year', leave.date_to))
        """
    )
    # Create allocations for those that are still missing their holiday_allocation_id
    # Helper column
    util.create_column(cr, "hr_leave_allocation", "_tmp_leave_id", "integer")
    cr.execute(
        """
        WITH helper AS (
            INSERT INTO hr_leave_allocation (
                private_name,
                employee_id, date_from,
                date_to,
                number_of_days, holiday_status_id, state, holiday_type,
                allocation_type,
                _tmp_leave_id
            )
            SELECT CONCAT('Correction: Missing Allocation for ', employee.name),
                    employee.id, date_trunc('year', leave.date_to),
                    (date_trunc('year', leave.date_from) + INTERVAL '1 year' - INTERVAL '1 day'),
                    leave.number_of_days, leave.holiday_status_id, 'validate', 'employee',
                    'regular',
                    leave.id
              FROM hr_leave leave
              JOIN hr_employee employee
                ON employee.id = leave.employee_id
              JOIN hr_leave_type leave_type
                ON leave_type.id = leave.holiday_status_id
             WHERE leave.holiday_allocation_id IS NULL
               AND leave_type.requires_allocation = 'yes'
         RETURNING id, _tmp_leave_id, private_name
        )
        UPDATE hr_leave leave
           SET holiday_allocation_id = h.id
          FROM helper h
         WHERE h._tmp_leave_id = leave.id
     RETURNING leave.holiday_allocation_id, h.private_name
        """
    )
    if cr.rowcount:
        msg = """
        <details>
            <summary>
            Due to an invalid configuration of leaves the following allocations had to be created.
            </summary>
            <ul>{}</ul>
        </details>
        """.format(
            "\n".join(
                "<li>{}</li>".format(
                    util.get_anchor_link_to_record(
                        "hr.leave.allocation", row["holiday_allocation_id"], row["private_name"]
                    )
                )
                for row in cr.dictfetchall()
            ),
        )
        util.add_to_migration_reports(msg, format="html", category="Human Resources")
    util.remove_column(cr, "hr_leave_allocation", "_tmp_leave_id")

    # Remove Columns
    util.remove_field(cr, "hr.leave.allocation", "first_approver_id")
    util.remove_field(cr, "hr.leave.allocation", "second_approver_id")
    util.remove_field(cr, "hr.leave.allocation", "accrual_limit")
    util.remove_field(cr, "hr.leave.allocation", "number_per_interval")
    util.remove_field(cr, "hr.leave.allocation", "interval_number")
    util.remove_field(cr, "hr.leave.allocation", "unit_per_interval")
    util.remove_field(cr, "hr.leave.allocation", "interval_unit")
    util.remove_field(cr, "hr.leave.report", "payslip_status")
    util.remove_field(cr, "hr.leave.type", "code")
    util.rename_field(cr, "hr.leave.type", "valid", "has_valid_allocation")
    util.remove_field(cr, "hr.leave.type", "allocation_type")
    util.remove_field(cr, "hr.leave.type", "validity_stop")
    util.remove_field(cr, "hr.leave.type", "validity_start")

    util.remove_view(cr, "hr_holidays.hr_leave_report_kanban")
    util.remove_view(cr, "hr_holidays.hr_leave_allocation_view_form_dashboard")

    util.remove_field(
        cr, "hr.leave", "payslip_status", drop_column=not util.module_installed(cr, "hr_payroll_holidays")
    )

    # Drop constraints
    util.remove_constraint(cr, "hr_leave_allocation", "hr_leave_allocation_number_per_interval_check")
    util.remove_constraint(cr, "hr_leave_allocation", "hr_leave_allocation_interval_number_check")

    util.remove_record(cr, "hr_holidays.action_hr_holidays_dashboard")
    util.remove_record(cr, "hr_holidays.action_report_to_payslip")
