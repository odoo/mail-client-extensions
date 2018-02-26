# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'hr_expense', 'currency_company_id', 'int4')
    cr.execute("""
        UPDATE hr_expense e
           SET currency_company_id = s.currency_id
          FROM hr_expense_sheet s
         WHERE s.id = e.sheet_id
    """)

    util.create_column(cr, 'hr_expense', 'total_amount_company', 'numeric')
    cr.execute("""
        UPDATE hr_expense
           SET total_amount_company = total_amount
         WHERE currency_id = currency_company_id
    """)
