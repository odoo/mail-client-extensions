from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_expense.account_journal_dashboard_kanban_view_inherit_hr_expense")
    util.explode_execute(
        cr,
        """
        UPDATE hr_expense
           SET payment_mode = 'own_account'
         WHERE payment_mode IS NULL
        """,
        table="hr_expense",
    )

    util.create_column(cr, "res_company", "expense_outstanding_account_id", "int4")
    cr.execute(
        """
        UPDATE res_company
           SET expense_outstanding_account_id = account_journal_payment_credit_account_id
        """
    )
