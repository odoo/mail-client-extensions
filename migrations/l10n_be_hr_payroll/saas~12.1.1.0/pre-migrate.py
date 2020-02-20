# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_spouse_handicap")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_insufficient_other_net")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_insufficient_net")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_juniors")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_seniors")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_disabled")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_isolated_parent")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_reduction_isolated")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_salary_rule_other_family_charges_reductions")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_child")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_child_alw")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_baremeIII")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_baremeII")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss_2")
    util.remove_record(cr, "l10n_be_hr_payroll.hr_payroll_rules_mis_ex_onss_1")
