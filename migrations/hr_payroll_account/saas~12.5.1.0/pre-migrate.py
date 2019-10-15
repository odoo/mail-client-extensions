# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, 'hr_payslip', 'journal_id') # Yes, intended to not remove field
    util.create_column(cr, 'hr_salary_rule', 'not_computed_in_net', "boolean")
    util.remove_field(cr, "hr.contract", "journal_id")
    util.remove_field(cr, "hr.payslip.run", "journal_id")
    util.remove_view(cr, "hr_payroll_account.view_hr_payslip_inherit_form")
    util.remove_view(cr, "hr_payroll_account.hr_payslip_view_form")
    util.remove_view(cr, "hr_payroll_account.hr_contract_form_inherit")
    util.remove_view(cr, "hr_payroll_account.hr_payslip_run_form_inherit")
    util.remove_view(cr, "hr_payroll_account.hr_payslip_run_search_inherit")
    util.remove_view(cr, "hr_payroll_account.hr_payslip_run_tree_inherit")
    util.remove_view(cr, "hr_payroll_account.hr_salary_rule_form_inherit")
