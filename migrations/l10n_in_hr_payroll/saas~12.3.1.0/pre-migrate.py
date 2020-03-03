# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    salary_rule = util.splitlines(
        """
         hr_salary_rule_da
         hr_salary_rule_houserentallowancemetro_nonmetro
         hr_salary_trans_allownce
         hr_salary_rule_special
         hr_payroll_rule_child1
         hr_payroll_rule_child2
         hr_payroll_rule_city1
         hr_payroll_rule_metrocity
         hr_payroll_rule_nonmetrocity
         hr_salary_rule_arrears
         hr_salary_rule_lta
         hr_salary_rule_le
         hr_salary_rule_performance
         hr_salary_rule_bonus
         hr_salary_rule_medical_allow
         hr_salary_rule_medical
         hr_salary_rule_food_coupon
         hr_salary_rule_journals
         hr_salary_rule_uniform_senior
         hr_salary_rule_uniform_junior
         hr_salary_rule_telephone
         hr_salary_rule_prof_develope
         hr_payroll_rule_car
         hr_salary_rule_internet
         hr_salary_rule_driver
         hr_payslip_rule_tds
         hr_payslip_line_professional_tax
         hr_payslip_rule_epf
         hr_payslip_rule_enps
         hr_payslip_rule_vpf
         hr_payslip_rule_cpt
         hr_salary_rule_food_coupon_ded
         hr_payslip_rule_lwf_employee
         hr_payslip_rule_lwf_employer
         hr_payslip_rule_cgti
         hr_payslip_rule_dla
         hr_payslip_rule_cmt
         hr_payslip_rule_ode
         hr_payslip_rule_ernps
         hr_payslip_rule_erpf
    """
    )
    util.delete_unused(cr, *["l10n_in_hr_payroll.%s" % r for r in salary_rule])
