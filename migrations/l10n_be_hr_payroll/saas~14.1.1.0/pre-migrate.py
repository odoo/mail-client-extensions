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
