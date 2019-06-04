# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'hr_contract', 'structure_type_id', 'int4')
    util.rename_field(cr, "hr.leave.type", 'benefit_type_id', 'work_entry_type_id')
    util.create_column(cr, 'hr_payslip_line', 'partner_id', 'int4')
    util.create_column(cr, 'hr_payslip_line', 'date_from', 'date')
    util.create_column(cr, 'hr_payslip_line', 'date_to', 'date')
    util.create_column(cr, 'hr_payslip_line', 'company_id', 'int4')
    util.create_column(cr, 'hr_payroll_structure', 'type_id', 'int4')
    util.create_column(cr, 'hr_payroll_structure', 'regular_pay', 'boolean')
    util.create_column(cr, 'hr_salary_rule', 'struct_id', 'int4')
    util.create_column(cr, 'hr_salary_rule', 'partner_id', 'int4')
    if util.table_exists(cr, 'hr_benefit'):
        util.rename_model(cr, 'hr.benefit', 'hr.work.entry')
    util.rename_field(cr, "hr.work.entry", 'benefit_type_id', 'work_entry_type_id')
    if util.table_exists(cr, 'hr_benefit_type'):
        util.rename_model(cr, 'hr.benefit.type', 'hr.work.entry.type')
    if util.table_exists(cr, 'hr_user_benefit_employee'):
        util.rename_model(cr, 'hr.user.benefit.employee', 'hr.user.work.entry.employee')
    util.rename_field(cr, "resource.calendar.attendance", 'benefit_type_id', 'work_entry_type_id')
    util.rename_field(cr, "resource.calendar.leaves", 'benefit_type_id', 'work_entry_type_id')

    cr.execute("""
        UPDATE hr_payslip_line l
           SET partner_id=s.partner_id
          FROM hr_salary_rule s
         WHERE s.id=l.salary_rule_id
    """)
    cr.execute("""
        UPDATE hr_payslip_line l
           SET date_from=p.date_from,
               date_to=p.date_to,
               company_id=p.company_id
          FROM hr_payslip p
         WHERE p.id=l.slip_id
    """)
