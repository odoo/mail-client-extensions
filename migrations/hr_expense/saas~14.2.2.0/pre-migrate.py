# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
            UPDATE hr_expense
               SET currency_id = res_company.currency_id
              FROM res_company
             WHERE hr_expense.company_id = res_company.id
               AND hr_expense.currency_id IS NULL
        """
    )
    util.remove_column(cr, "hr_expense", "company_currency_id")  # not stored anymore
