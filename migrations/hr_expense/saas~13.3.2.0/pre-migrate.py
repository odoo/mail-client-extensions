# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense", "accounting_date", "date")
    cr.execute(
        """
        UPDATE hr_expense e
           SET accounting_date = s.accounting_date
          FROM hr_expense_sheet s
         WHERE s.id = e.sheet_id
    """
    )

    util.remove_record(cr, "hr_expense.access_account_invoice_user")
    util.remove_record(cr, "hr_expense.access_account_invoice_line_user")
