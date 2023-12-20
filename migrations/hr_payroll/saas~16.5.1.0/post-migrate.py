# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_payroll.default_gross_salary_rule", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_deduction_salary_rule", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_attachment_of_salary_rule", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_assignment_of_salary_rule", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_child_support", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_reimbursement_salary_rule", noupdate=False)
    util.force_noupdate(cr, "hr_payroll.default_net_salary", noupdate=False)

    util.update_record_from_xml(cr, "hr_payroll.default_gross_salary_rule")
    util.update_record_from_xml(cr, "hr_payroll.default_deduction_salary_rule")
    util.update_record_from_xml(cr, "hr_payroll.default_attachment_of_salary_rule")
    util.update_record_from_xml(cr, "hr_payroll.default_assignment_of_salary_rule")
    util.update_record_from_xml(cr, "hr_payroll.default_child_support")
    util.update_record_from_xml(cr, "hr_payroll.default_reimbursement_salary_rule")
    util.update_record_from_xml(cr, "hr_payroll.default_net_salary")

    # Replace master rules/categories/inputs that are coming from default values
    updates = {f"categories.{code}": f'categories["{code}"]' for code in ["BASIC", "ALW", "DED", "NET"]}
    updates.update(
        (f"inputs.{code}", f'inputs.get("{code}")')
        for code in ["ATTACH_SALARY", "ASSIG_SALARY", "CHILD_SUPPORT", "REIMBURSEMENT", "DEDUCTION"]
    )
    updates["rules.NET"] = "rules.get('NET')"

    fields = {
        field: util.pg_replace(field, updates.items())
        for field in [
            "amount_python_compute",
            "quantity",
            "amount_percentage_base",
            "condition_range",
            "condition_python",
        ]
    }

    query = "UPDATE hr_salary_rule SET " + ", ".join(f"{f} = {v}" for f, v in fields.items())

    util.explode_execute(cr, query, table="hr_salary_rule")
