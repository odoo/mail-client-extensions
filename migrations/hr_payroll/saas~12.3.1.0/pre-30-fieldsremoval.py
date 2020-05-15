# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "struct_id")
    util.remove_field(cr, "hr.payslip.line", "register_id")
    util.remove_field(cr, 'hr.payroll.structure', 'code')
    util.remove_field(cr, 'hr.payroll.structure', 'parent_id')
    util.remove_field(cr, 'hr.payroll.structure', 'children_ids')

    # field `rule_ids` is now a o2m. Drop m2m table
    cr.execute("DROP TABLE hr_structure_salary_rule_rel")

    util.remove_field(cr, 'hr.salary.rule', 'parent_rule_id')
    util.remove_field(cr, 'hr.salary.rule', 'child_ids')
    util.remove_field(cr, 'hr.salary.rule', 'register_id')

    util.remove_model(cr, 'hr.contribution.register')
    util.remove_model(cr, 'payslip.lines.contribution.register')
    util.remove_model(cr, "report.hr_payroll.report_contributionregister")
