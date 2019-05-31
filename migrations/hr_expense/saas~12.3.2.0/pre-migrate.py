# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_expense.ir_rule_hr_expense_{user,approver}"))
    util.rename_xmlid(cr, *eb("hr_expense.ir_rule_hr_expense_sheet_{user,approver}"))
