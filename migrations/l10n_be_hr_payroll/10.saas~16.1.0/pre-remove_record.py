# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        "hr_salary_rule",
        [
            "l10n_be_hr_payroll.hr_payroll_rules_p_p_b1",
            "l10n_be_hr_payroll.hr_payroll_rules_child_handicap",
            "l10n_be_hr_payroll.hr_payroll_rules_company_car_parent",
            "l10n_be_hr_payroll.hr_payroll_rules_company_car_emp",
            "l10n_be_hr_payroll.hr_payroll_rules_parent_ch",
            "l10n_be_hr_payroll.hr_payroll_rules_ch_value",
            "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss",
            "l10n_be_hr_payroll.hr_payroll_rules_insurance",
            "l10n_be_hr_payroll.hr_payroll_rules_advantage",
        ],
    )

    util.remove_field(cr, 'hr.contract', 'travel_reimbursement_amount')
    util.remove_field(cr, 'hr.contract', 'car_company_amount')
    util.remove_field(cr, 'hr.contract', 'car_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'misc_onss_deduction')
    util.remove_field(cr, 'hr.contract', 'meal_voucher_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'insurance_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'misc_advantage_amount')

    util.remove_view(cr, 'l10n_be_hr_payroll.hr_contract_form_l10n_be_inherit')
