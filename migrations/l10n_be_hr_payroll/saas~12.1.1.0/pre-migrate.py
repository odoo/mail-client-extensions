# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_spouse_handicap")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_insufficient_other_net")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_insufficient_net")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_juniors")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_seniors")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_disabled")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_isolated_parent")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_isolated")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_salary_rule_other_family_charges_reductions")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_child")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_child_alw")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_baremeIII")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_baremeII")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss_2")
    util.delete_unused(cr, "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss_1")
