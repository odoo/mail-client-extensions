# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.remove_view(cr, "l10n_be_hr_payroll.hr_payslip_run_tree")

    util.create_column(cr, "hr_leave_allocation", "max_leaves_allocated", "float8", default=20)

    util.create_column(cr, "hr_payroll_alloc_paid_leave", "year", "integer")
    util.remove_field(cr, "hr.payroll.alloc.paid.leave", "date_start")
    util.remove_field(cr, "hr.payroll.alloc.paid.leave", "date_end")
    util.remove_field(cr, "hr.payroll.alloc.paid.leave", "alloc_employee_ids", cascade=True)

    util.remove_field(cr, "hr.payroll.alloc.employee", "worked_days")
    util.remove_field(cr, "hr.payroll.alloc.employee", "paid_time_off")
    util.create_column(cr, "hr_payroll_alloc_employee", "paid_time_off", "float8")
    util.create_column(cr, "hr_payroll_alloc_employee", "paid_time_off_to_allocate", "float8")

    util.remove_field(cr, "l10n_be.hr.payroll.credit.time.wizard", "work_time")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "time_off_allocation", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "remaining_allocated_time_off", "float8")

    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "time_off_allocation", "float8")
    util.create_column(cr, "l10n_be_hr_payroll_exit_credit_time_wizard", "remaining_allocated_time_off", "float8")

    util.drop_depending_views(cr, "hr_contract", "work_time_rate")
    cr.execute("ALTER TABLE hr_contract ALTER COLUMN work_time_rate TYPE float8 USING work_time_rate::float8")
    # Drop selection values associated with hr.contract.work_time_rate
    cr.execute("""
        DELETE
          FROM ir_model_fields_selection
         WHERE field_id = (
            SELECT id
              FROM ir_model_fields
             WHERE name = 'work_time_rate' AND model = 'hr.contract'
        )
    """)

    # Before this commit and related community and enterprise PR commits, the time credit contracts were using
    # the time_credit_type_id field of their structure_type_id field in order to find the work entry type to use for
    # credit time work entries. The goal of the PR is to let the user choose the work item type in the
    # credit time wizard. The field is thus moved into the l10n_be.hr.payroll.credit.time.wizard and hr.contract models.
    # That's why we need to migrate that information.
    util.create_column(cr, "hr_contract", "time_credit_type_id", "int4")
    util.create_column(cr, "l10n_be_hr_payroll_credit_time_wizard", "time_credit_type_id", "int4")
    cr.execute("""
        UPDATE hr_contract c
           SET time_credit_type_id = st.time_credit_type_id
          FROM hr_payroll_structure_type AS st
         WHERE c.structure_type_id = st.id
           AND c.time_credit = true
    """)
    util.remove_view(cr, "l10n_be_hr_payroll.hr_payroll_structure_type_view_form")
    util.remove_field(cr, "hr.payroll.structure.type", "time_credit_type_id")
