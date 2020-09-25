# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_expense.action_approved_expense")
    util.remove_record(cr, "hr_expense.hr_expense_action")
    util.remove_record(cr, "hr_expense.action_request_to_pay_expense_sheet")
