# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'hr_expense.view_expenses_form', 'hr_expense.hr_expense_form_view')
