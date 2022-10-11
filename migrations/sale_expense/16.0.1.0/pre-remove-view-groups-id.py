# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_expense.hr_expense_form_view_inherit_account_manager")
    util.remove_view(cr, "sale_expense.hr_expense_form_view_inherit_saleman")
