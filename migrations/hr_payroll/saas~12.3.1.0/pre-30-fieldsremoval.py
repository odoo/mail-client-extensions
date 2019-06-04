# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr_contract", 'struct_id')
    util.remove_field(cr, 'hr_payslip_line', 'register_id', 'int4')
    util.remove_field(cr, 'hr.payroll.structure', 'code')
    util.remove_field(cr, 'hr.payroll.structure', 'parent_id')
    util.remove_field(cr, 'hr.payroll.structure', 'children_ids')
    util.remove_field(cr, 'hr.payroll.structure', 'rule_ids')

    util.remove_field(cr, 'hr.salary.rule', 'parent_rule_id')
    util.remove_field(cr, 'hr.salary.rule', 'child_ids')
    util.remove_field(cr, 'hr.salary.rule', 'register_id')

    util.remove_model(cr, 'hr.contribution.register')
    util.remove_model(cr, 'payslip.lines.contribution.register')
