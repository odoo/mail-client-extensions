# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_maj")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_employee")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_onss_rule")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_employment_bonus_employees")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_employment_bonus_workers")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_gross_with_ip")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_ip_part")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_bareme")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_p_p")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_bonus_pay_p_p")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_parent_company_car")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_atn_internet")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_atn_mobile")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_company_car_2")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_atn_internet_2")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_atn_mobile_2")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_commission_on_target")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_ch_worker")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_reim_travel")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_representation_fees")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_ip")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_ip_deduction")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_suppl_net")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_retained_net")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_basic")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_salary")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_gross")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_double_holiday_pay_net")
    for struct in [
        "l10n_be_hr_payroll.hr_payroll_salary_structure_employee",
        "l10n_be_hr_payroll.hr_payroll_salary_structure_worker",
        "l10n_be_hr_payroll.hr_payroll_salary_structure_double_holiday_pay",
        "l10n_be_hr_payroll.hr_payroll_salary_structure_end_of_year_bonus",
    ]:
        struct_id = util.ref(cr, struct)
        if struct_id:
            # the rule is deleted only if not linked to a payslip line through the salary_rule_id fk
            # with a 'not null' constraint
            cr.execute(
                """
                DELETE
                  FROM hr_salary_rule r
                 WHERE r.struct_id=%s
                   AND NOT EXISTS (SELECT 1
                                     FROM hr_payslip_line l
                                    WHERE l.salary_rule_id = r.id)
                """,
                [struct_id],
            )
        util.delete_unused(cr, struct)

    cr.execute("UPDATE hr_work_entry_type SET meal_voucher=FALSE")
    cr.execute("UPDATE hr_contract SET fiscal_voluntarism=FALSE,fiscal_voluntary_rate=0")
