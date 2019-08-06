# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_urssaf_register')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_retraite_register')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_cci_register')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_prevoyance_register')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_secu')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_tranche_a')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_tranche_b')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_tranche_c')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_tranche_1')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_tranche_2')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_total_charges_salariales')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_total_retenues')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_cumul_imposable')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_total_charges_patronales')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_rule_total')
    for r in ('1', '2', '3', '4', '10', '11', '12', '13', '14', '15', '16', '17',
              '38', '39', '18', '19', '20', '21', '5', '35', '36', '37', '40',
              '7', '8', '9', '22', '23', '24', '25', '26', '27', '28', '29',
              '30'):
        for s in ('', 'r'):
            util.remove_record(cr, 'l10n_fr_hr_payroll.hr_payroll_rules_%s_employe%s' % (r, s))
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_payroll_salary_structure_base')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_payroll_salary_structure_employe_non_cadre')
    util.remove_record(cr, 'l10n_fr_hr_payroll.hr_payroll_salary_structure_employe_cadre')
