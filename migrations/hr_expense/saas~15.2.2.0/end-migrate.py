# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.recompute_fields(cr, "hr.expense", ["untaxed_amount", "amount_tax", "amount_tax_company"])

    cr.execute(
        """
            With totals AS (
                    SELECT s.id, sum(e.total_amount_company) as total, sum(e.amount_tax_company) as tax
                      FROM hr_expense_sheet s
                      JOIN hr_expense e ON e.sheet_id = s.id
                     GROUP BY s.id
            )
            UPDATE hr_expense_sheet s
               SET total_amount = t.total, total_amount_taxes = t.tax, untaxed_amount = t.total - t.tax
              FROM totals t
             WHERE s.id = t.id;
        """
    )
