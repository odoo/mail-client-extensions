# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
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
