# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #Rules without struct_id are not last level Rules, then can be deleted
    cr.execute("""
        SELECT imd.module,imd.name
        FROM hr_salary_rule r
        JOIN ir_model_data imd ON r.id = imd.res_id
                                  AND imd.model = 'hr.salary.rule'
   LEFT JOIN hr_payslip_line p ON p.salary_rule_id=r.id
        WHERE r.struct_id IS NULL
          AND imd.module in ('hr_payroll', 'l10n_be_hr_payroll')
          AND p.id IS NULL
    """)
    for name in cr.fetchall():
        util.remove_record(cr, name[0] + '.' + name[1])

    env = util.env(cr)
    loaded_xmlids = env['ir.model'].pool.loaded_xmlids
    hsr_xmlids = env['ir.model.data'].search([('model', '=', 'hr.salary.rule')])

    for rule in hsr_xmlids:
        xmlid = '%s.%s' % (rule.module, rule.name)
        if xmlid not in loaded_xmlids:
            cr.execute("""
                SELECT count(*) FROM hr_payslip_line WHERE salary_rule_id = %s
            """ % rule.res_id)
            cnt = cr.fetchone()[0]
            if cnt > 0:
                env['hr.salary.rule'].browse(rule.res_id).active = False
                util.force_noupdate(cr, xmlid)
