# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "has_negative_net_to_report", "boolean")
    util.create_column(cr, "hr_payslip", "edited", "boolean")

    # Related fields that become stored
    util.create_column(cr, "hr_payslip_worked_days", "name", "varchar")
    cr.execute(
        """UPDATE hr_payslip_worked_days hpwd
           SET name=hwet.name
           FROM hr_work_entry_type hwet
           WHERE hpwd.work_entry_type_id = hwet.id"""
    )

    util.create_column(cr, "hr_payslip_input", "name", "varchar")
    cr.execute(
        """UPDATE hr_payslip_input hpi
           SET name=hpit.name
           FROM hr_payslip_input_type hpit
           WHERE hpi.input_type_id = hpit.id"""
    )

    # transients models
    # This field was defined in the `l10n_be_hr_payroll_variable_revenue` module (merged in `l10n_be_hr_payroll`)
    util.move_field_to_module(cr, "hr.payslip.emplees", "department_id", "l10n_be_hr_payroll", "hr_payroll")
    util.create_column(cr, "hr_payslip_employees", "department_id", "int4")

    eb = util.expand_braces
    util.rename_xmlid(cr, "hr_payroll.action_view_account_move_line_reconcile", "hr_payroll.action_reset_work_entries")
    util.rename_xmlid(cr, *eb("{l10n_be_,}hr_payroll.input_deduction"))
    util.rename_xmlid(cr, *eb("{l10n_be_,}hr_payroll.input_reimbursement"))
