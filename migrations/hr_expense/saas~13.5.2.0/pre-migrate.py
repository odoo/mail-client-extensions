# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense", "sample", "boolean", default=False)
    util.create_column(cr, "hr_expense_sheet", "amount_residual", "numeric")

    # Compute the residual amount on expense sheets using the same currency as the one from the company.
    cr.execute(
        """
            WITH cte AS (
                SELECT s.id, -ROUND(SUM(
                    CASE WHEN s.currency_id = c.currency_id
                        THEN l.amount_residual
                        ELSE l.amount_residual_currency
                         END
                    ), curr.decimal_places) AS residual
                FROM hr_expense_sheet s
                JOIN res_company c ON c.id = s.company_id
                JOIN res_currency curr ON curr.id = s.currency_id
                JOIN account_move_line l ON l.move_id = s.account_move_id
                JOIN account_account account ON account.id = l.account_id
               WHERE account.internal_type IN ('receivable', 'payable')
            GROUP BY s.id, curr.decimal_places
            )
            UPDATE hr_expense_sheet s
               SET amount_residual = cte.residual
              FROM cte
             WHERE cte.id = s.id
        """
    )

    util.remove_model(cr, "hr.expense.sheet.register.payment.wizard")

    util.rename_xmlid(cr, "hr_expense.view_expenses_tree", "hr_expense.hr_expense_view_expenses_analysis_tree")
    util.rename_xmlid(cr, "hr_expense.view_expense_kanban_view", "hr_expense.hr_expense_view_expenses_analysis_kanban")

    util.remove_record(cr, "hr_expense.action_unsubmitted_expense")
    util.remove_record(cr, "hr_expense.action_request_approve_expense_sheet")
    util.remove_record(cr, "hr_expense.action_request_to_post_expense_sheet")
