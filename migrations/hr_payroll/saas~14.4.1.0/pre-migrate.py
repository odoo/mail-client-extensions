# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "queued_for_pdf", "bool", default=False)
    util.convert_field_to_html(cr, "hr.salary.rule.category", "note")
    util.convert_field_to_html(cr, "hr.rule.parameter", "description")
    util.convert_field_to_html(cr, "hr.salary.rule", "note")
    util.convert_field_to_html(cr, "hr.payroll.structure", "note")
