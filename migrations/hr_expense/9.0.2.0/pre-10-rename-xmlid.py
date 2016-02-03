# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'hr_expense.view_expenses_form', 'hr_expense.hr_expense_form_view')

    forces = util.splitlines("""
        view_expenses_tree
        hr_expense_form_view
        view_hr_expense_filter
        expense_all
        view_product_hr_expense_form

        action_approved_expense
        action_request_approve_expense

        menu_expense_approved
        menu_hr_product
        menu_expense_all
        menu_expense_to_approve

        report_expense
    """)
    for f in forces:
        util.force_noupdate(cr, 'hr_expense.' + f, False)
