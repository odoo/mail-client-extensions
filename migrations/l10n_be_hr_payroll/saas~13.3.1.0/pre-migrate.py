# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    # Removed fields
    removed_fields = {
        "hr.contract": ["country_code", "transport_employer_cost", "ucm_insurance", "transport_mode_others"],
    }
    for model, fields in removed_fields.items():
        for field in fields:
            util.remove_field(cr, model, field)
    util.create_column(cr, "hr_payroll_structure_type", "time_credit_type_id", "int4")
    util.create_column(cr, "hr_payslip_worked_days", "is_credit_time", "boolean")
    util.create_column(cr, "hr_work_entry", "is_credit_time", "boolean")

    util.delete_unused(cr, "l10n_be_hr_payroll.structure_type_employee_cp200_pfi")
