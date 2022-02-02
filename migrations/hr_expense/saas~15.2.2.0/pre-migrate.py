# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.expense", "label_total_amount_company")

    util.create_column(cr, "hr_expense", "untaxed_amount", "numeric")
    util.create_column(cr, "hr_expense", "amount_tax", "numeric")
    util.create_column(cr, "hr_expense", "amount_tax_company", "numeric")

    util.create_column(cr, "res_company", "expense_journal_id", "int4")

    util.create_column(cr, "hr_expense_sheet", "untaxed_amount", "numeric")
    util.create_column(cr, "hr_expense_sheet", "total_amount_taxes", "numeric")
