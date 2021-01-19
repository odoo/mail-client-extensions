# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Keep data
    util.force_noupdate(cr, "l10n_be_hr_payroll.cp200_employees_salary_deduction", True)
    util.force_noupdate(cr, "l10n_be_hr_payroll.cp200_employees_salary_reimbursement", True)

    # models
    util.create_column(cr, "hr_leave_allocation", "max_leaves_allocated", "float8", default=20)

    util.drop_depending_views(cr, "hr_contract", "work_time_rate")
    cr.execute("ALTER TABLE hr_contract ALTER COLUMN work_time_rate TYPE float8 USING work_time_rate::float8")
    # Drop selection values associated with hr.contract.work_time_rate
    cr.execute(
        """
        DELETE
          FROM ir_model_fields_selection
         WHERE field_id = (
            SELECT id
              FROM ir_model_fields
             WHERE name = 'work_time_rate' AND model = 'hr.contract'
        )
    """
    )

    util.create_column(cr, "hr_contract", "time_credit_full_time_wage", "numeric")
    cr.execute(
        """
            UPDATE hr_contract
               SET time_credit_full_time_wage = CASE WHEN time_credit AND work_time_rate != 0
                                                     THEN wage / work_time_rate
                                                     ELSE wage
                                                 END
        """
    )

    # Before this commit and related community and enterprise PR commits, the time credit contracts were using
    # the time_credit_type_id field of their structure_type_id field in order to find the work entry type to use for
    # credit time work entries. The goal of the PR is to let the user choose the work item type in the
    # credit time wizard. The field is thus moved into the l10n_be.hr.payroll.credit.time.wizard and hr.contract models.
    # That's why we need to migrate that information.
    util.create_column(cr, "hr_contract", "time_credit_type_id", "int4")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "time_credit_type_id", "int4")
    cr.execute(
        """
        UPDATE hr_contract c
           SET time_credit_type_id = st.time_credit_type_id
          FROM hr_payroll_structure_type AS st
         WHERE c.structure_type_id = st.id
           AND c.time_credit = true
    """
    )
    util.remove_field(cr, "hr.payroll.structure.type", "time_credit_type_id")
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payroll_structure_type_view_form")

    # remove views from merged module `l10n_be_hr_payroll_variable_revenue`
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_employees_view_form")
    if not util.module_installed(cr, "hr_payroll_holidays"):
        util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_tree")

    # Move fields from l10n_be_hr_payroll_posted_employee. The module has been merged into
    # hr_work_entry_contract on the base pre-module script.
    util.move_field_to_module(cr, "hr.contract", "no_onss", "hr_work_entry_contract", "l10n_be_hr_payroll")
    util.create_column(cr, "hr_contract", "no_onss", "boolean")
    util.move_field_to_module(cr, "hr.contract", "no_withholding_taxes", "hr_work_entry_contract", "l10n_be_hr_payroll")
    util.create_column(cr, "hr_contract", "no_withholding_taxes", "boolean")

    # fields from l10n_be_hr_payroll_proration module (that may not be installed, even if auto_install)
    util.create_column(cr, "hr_work_entry_type", "private_car", "boolean")
    util.create_column(cr, "hr_work_entry_type", "representation_fees", "boolean")

    # Wizards
    util.create_column(cr, "hr_payroll_alloc_paid_leave", "department_id", "integer")
    util.create_column(cr, "hr_payroll_alloc_paid_leave", "year", "varchar")
    util.remove_field(cr, "hr.payroll.alloc.paid.leave", "date_start")
    util.remove_field(cr, "hr.payroll.alloc.paid.leave", "date_end")
    # field is now a o2m instead of m2m. remove the relation table
    cr.execute("DROP TABLE IF EXISTS hr_payroll_alloc_employee_hr_payroll_alloc_paid_leave_rel")

    util.remove_field(cr, "hr.payroll.alloc.employee", "worked_days")
    cr.execute("ALTER TABLE hr_payroll_alloc_employee ALTER COLUMN paid_time_off TYPE float8")
    util.create_column(cr, "hr_payroll_alloc_employee", "paid_time_off_to_allocate", "float8")
    util.create_column(cr, "hr_payroll_alloc_employee", "contract_next_year_id", "int4")
    util.create_column(cr, "hr_payroll_alloc_employee", "alloc_paid_leave_id", "int4")

    util.remove_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "work_time")  # field not related (and change type)
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "date_start", "date")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "date_end", "date")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "time_off_allocation", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "remaining_allocated_time_off", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "holiday_status_id", "int4")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "leave_allocation_id", "int4")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "time_credit_type_id", "int4")

    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "time_off_allocation", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "remaining_allocated_time_off", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "remaining_allocated_time_off", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "holiday_status_id", "int4")
    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "leave_allocation_id", "int4")
