# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb('hr.expense{,.sheet}.register.payment.wizard'))
    util.rename_xmlid(cr, *eb('hr_expense.hr_expense{,_sheet}_register_payment_view_form'))
    util.rename_xmlid(cr, *eb('hr_expense.hr_expense{,_sheet}_register_payment_wizard_action'))
