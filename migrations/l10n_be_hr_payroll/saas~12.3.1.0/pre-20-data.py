# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_maj')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_employee')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_onss_rule')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_employment_bonus_employees')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_employment_bonus_workers')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_gross_with_ip')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_ip_part')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_bareme')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_p_p')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_bonus_pay_p_p')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_parent_company_car')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_atn_internet')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_atn_mobile')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_company_car_2')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_atn_internet_2')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_atn_mobile_2')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_commission_on_target')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_ch_worker')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_reim_travel')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_representation_fees')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_ip')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_ip_deduction')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_suppl_net')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_payroll_rules_retained_net')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_basic')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_salary')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_gross')
    util.remove_record(cr, 'l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_net')
    for struct in ['l10n_be_hr_payroll.hr_payroll_salary_structure_employee',
                   'l10n_be_hr_payroll.hr_payroll_salary_structure_worker',
                   'l10n_be_hr_payroll.hr_payroll_salary_structure_double_holiday_pay',
                   'l10n_be_hr_payroll.hr_payroll_salary_structure_end_of_year_bonus']:
        struct_id = util.ref(cr, struct)
        if struct_id:
            cr.execute("DELETE FROM hr_salary_rule where struct_id=%s", [struct_id, ])
        util.remove_record(cr, struct)

    cr.execute("UPDATE hr_work_entry_type SET meal_voucher=FALSE")
    cr.execute("UPDATE hr_contract SET fiscal_voluntarism=FALSE,fiscal_voluntary_rate=0")
