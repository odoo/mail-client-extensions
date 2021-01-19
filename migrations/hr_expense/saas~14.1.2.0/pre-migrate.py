# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_expense.hr_expense_sheet_approve_action_server")
    util.remove_record(cr, "hr_expense.hr_expense_sheet_post_action_server")
    util.remove_record(cr, "hr_expense.action_expense_sheet_register_payment")
