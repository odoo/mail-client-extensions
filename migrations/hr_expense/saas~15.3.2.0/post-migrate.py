# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_expense.ir_rule_hr_expense_approver")
    util.update_record_from_xml(cr, "hr_expense.ir_rule_hr_expense_sheet_approver")
    util.update_record_from_xml(cr, "hr_expense.ir_rule_hr_expense_sheet_employee")
