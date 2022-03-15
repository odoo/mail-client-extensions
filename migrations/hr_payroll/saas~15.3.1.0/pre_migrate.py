# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_salary_rule", "appears_on_employee_cost_dashboard", "boolean", default=False)
    util.remove_view(cr, "hr_payroll.note_note_view_form_hr_payroll")
    util.remove_record(cr, "hr_payroll.note_note_hr_payroll_action")
