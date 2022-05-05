# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll.hr_rule_parameter_value_view_form")

    cr.execute(
        """
        UPDATE hr_payroll_structure_type pst
           SET name = initcap(wage_type || ' fixed wage paid ' || default_schedule_pay)
         WHERE pst.name IS NULL
    """
    )

    fields = ["time_credit", "work_time_rate", "standard_calendar_id", "time_credit_full_time_wage"]
    for field in fields:
        util.move_field_to_module(cr, "hr.contract.history", field, "l10n_be_hr_payroll", "hr_payroll")
        util.move_field_to_module(cr, "hr.contract", field, "l10n_be_hr_payroll", "hr_payroll")

    util.move_field_to_module(cr, "hr.contract", "time_credit_type_id", "l10n_be_hr_payroll", "hr_payroll")

    if util.create_column(cr, "hr_contract", "time_credit_full_time_wage", "numeric"):
        cr.execute("UPDATE hr_contract SET time_credit_full_time_wage = wage")
    if util.create_column(cr, "hr_contract", "standard_calendar_id", "int4"):
        cr.execute("UPDATE hr_contract SET standard_calendar_id = resource_calendar_id")
    util.create_column(cr, "hr_contract", "time_credit_type_id", "int4")
    util.create_column(cr, "hr_contract", "work_time_rate", "float8", default=1)
