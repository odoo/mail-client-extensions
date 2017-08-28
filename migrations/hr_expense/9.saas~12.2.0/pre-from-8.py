# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'hr_expense_expense'):
        return

    # it's a migration from version 8.0
    # get back the old sheets

    util.rename_model(cr, 'hr.expense.expense', 'hr.expense.sheet')

    # remove draft sheets
    cr.execute("DELETE FROM hr_expense_sheet WHERE state='draft' RETURNING id")
    cr.execute("UPDATE hr_expense SET sheet_id = NULL WHERE sheet_id=ANY(%s)",
               [list(s for s, in cr.fetchall())])

    util.rename_field(cr, 'hr.expense.sheet', "date", "accounting_date")
    util.rename_field(cr, 'hr.expense.sheet', "user_valid", "responsible_id")
    util.rename_field(cr, 'hr.expense.sheet', "amount", "total_amount")

    old_fields = util.splitlines("""
        date_valid
        date_confirm
        user_id
        note
        ref
        invoice_id
        voucher_id
        employee_payable_account_id
    """)
    for f in old_fields:
        util.remove_column(cr, 'hr_expense_sheet', f)

    util.create_column(cr, 'hr_expense_sheet', 'bank_journal_id', 'int4')
    cr.execute("""
        WITH banks AS (
            SELECT company_id, (array_agg(id ORDER BY sequence, type, code))[1] as id
              FROM account_journal
             WHERE type IN ('bank', 'cash')
          GROUP BY company_id
        )
        UPDATE hr_expense_sheet s
           SET bank_journal_id = b.id
          FROM banks b
         WHERE b.company_id = s.company_id
    """)

    cr.execute("""
        UPDATE hr_expense_sheet
           SET state = CASE WHEN state = 'cancelled' THEN 'cancel'
                            WHEN state = 'confirm' THEN 'submit'
                            WHEN state = 'accepted' THEN 'approve'
                            WHEN state = 'done' THEN 'post'
                            WHEN state = 'paid' THEN 'done'
                            ELSE state END
    """)
