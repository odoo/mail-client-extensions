# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    moved = """
        hr_payroll_structure_cp200_structure_warrant
        cp200_other_input_warrant

        cp200_employees_salary_atn_warrant_p_p
        cp200_employees_salary_warrant_deduction
        cp200_employees_salary_inverse_atn_warrant
    """
    for xid in util.splitlines(moved):
        util.rename_xmlid(cr, f"l10n_be_hr_payroll_variable_revenue.{xid}", f"l10n_be_hr_payroll.{xid}")
