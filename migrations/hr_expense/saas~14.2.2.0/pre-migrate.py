# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            UPDATE hr_expense
               SET currency_id = res_company.currency_id
              FROM res_company
             WHERE hr_expense.currency_id IS NULL AND hr_expense.company_id = res_company.id
        """
    )
