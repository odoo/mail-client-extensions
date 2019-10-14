# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    xmlids = [
        'l10n_fr_hr_payroll.hr_urssaf_register',
        'l10n_fr_hr_payroll.hr_retraite_register',
        'l10n_fr_hr_payroll.hr_cci_register',
        'l10n_fr_hr_payroll.hr_prevoyance_register',
        'l10n_fr_hr_payroll.hr_rule_secu',
        'l10n_fr_hr_payroll.hr_rule_tranche_a',
        'l10n_fr_hr_payroll.hr_rule_tranche_b',
        'l10n_fr_hr_payroll.hr_rule_tranche_c',
        'l10n_fr_hr_payroll.hr_rule_tranche_1',
        'l10n_fr_hr_payroll.hr_rule_tranche_2',
        'l10n_fr_hr_payroll.hr_rule_total_charges_salariales',
        'l10n_fr_hr_payroll.hr_rule_total_retenues',
        'l10n_fr_hr_payroll.hr_rule_cumul_imposable',
        'l10n_fr_hr_payroll.hr_rule_total_charges_patronales',
        'l10n_fr_hr_payroll.hr_rule_total',
    ]
    util.delete_unused(cr, 'hr_payslip_line', xmlids)
    xmlids = []
    for r in ('1', '2', '3', '4', '10', '11', '12', '13', '14', '15', '16', '17',
              '38', '39', '18', '19', '20', '21', '5', '35', '36', '37', '40',
              '7', '8', '9', '22', '23', '24', '25', '26', '27', '28', '29',
              '30'):
        for s in ('', 'r'):
            xmlids.append('l10n_fr_hr_payroll.hr_payroll_rules_%s_employe%s' % (r, s))
    util.delete_unused(cr, 'hr_payslip_line', xmlids)
    for struct in ['l10n_fr_hr_payroll.hr_payroll_salary_structure_base',
                   'l10n_fr_hr_payroll.hr_payroll_salary_structure_employe_non_cadre',
                   'l10n_fr_hr_payroll.hr_payroll_salary_structure_employe_cadre']:
        struct_id = util.ref(cr, struct)
        if struct_id:
            cr.execute("SELECT imd.name FROM hr_salary_rule r JOIN ir_model_data imd on r.id = imd.res_id and imd.model = 'hr.salary.rule' WHERE r.struct_id=%s", [struct_id, ])
            for name in cr.fetchall():
                util.delete_unused(cr, 'hr_payslip_line' , ['hr_salary_rule.' + name[0]])
        util.delete_unused(cr, 'hr_salary_rule', [struct])
