# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'hr_expense.mt_expense_confirmed')
    util.remove_record(cr, 'hr_expense.mt_expense_responsible')
    util.remove_record(cr, 'hr_expense.mt_department_expense_confirmed')
