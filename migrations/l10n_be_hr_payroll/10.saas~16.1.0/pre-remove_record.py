# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_p_p_b1')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_child_handicap')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_company_car_parent')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_company_car_emp')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_parent_ch')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_ch_value')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_insurance')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_advantage')

    # Demo data -> To keep ?
    util.remove_record(cr, 'hr_payroll.hr_contract_firstcontract1')
    util.remove_record(cr, 'hr_payroll.hr_employee_payroll')
    util.remove_record(cr, 'l10n_be_hr_payroll.res_partner_onss')
    util.remove_record(cr, 'l10n_be_hr_payroll.res_partner_pp')

    util.remove_field(cr, 'hr.contract', 'travel_reimbursement_amount')
    util.remove_field(cr, 'hr.contract', 'car_company_amount')
    util.remove_field(cr, 'hr.contract', 'car_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'misc_onss_deduction')
    util.remove_field(cr, 'hr.contract', 'meal_voucher_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'insurance_employee_deduction')
    util.remove_field(cr, 'hr.contract', 'misc_advantage_amount')

    util.remove_view(cr, 'l10n_be_hr_payroll.hr_contract_form_l10n_be_inherit')
