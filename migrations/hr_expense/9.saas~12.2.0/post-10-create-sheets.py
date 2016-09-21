# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # field `accounting_date` has only been added in saas~11.
    # ensure the column exists (even we will remove it directly) to avoid complex query definition
    util.create_column(cr, 'hr_expense', 'accounting_date', 'date')

    # and fill it with move date.
    cr.execute("""
        UPDATE hr_expense e
           SET accounting_date = m.date
          FROM account_move m
         WHERE m.id = e.account_move_id
           AND accounting_date IS NULL
    """)

    util.create_column(cr, 'hr_expense_sheet', '_tmp', 'int4')
    cr.execute("""
        INSERT INTO hr_expense_sheet(_tmp, name, state, employee_id, address_id,
                                     total_amount, company_id, currency_id,
                                     journal_id, bank_journal_id, accounting_date,
                                     account_move_id, department_id,
                                     create_uid, write_uid, create_date, write_date)
             SELECT x.id, x.name, x.state, x.employee_id, e.address_home_id,
                    x.total_amount, x.company_id, x.currency_id,
                    x.journal_id, x.bank_journal_id, x.accounting_date,
                    x.account_move_id, x.department_id,
                    x.create_uid, x.write_uid, x.create_date, x.write_date
               FROM hr_expense x
               JOIN hr_employee e ON (e.id = x.employee_id)
              WHERE x.state != 'draft'
                AND x.sheet_id IS NULL
           ORDER BY x.id
    """)
    cr.execute("""
        UPDATE hr_expense x
           SET sheet_id = s.id,
               state = CASE WHEN s.state = 'cancel' THEN 'refused'
                            WHEN s.account_move_id IS NULL THEN 'reported'
                            ELSE 'done'
                        END
          FROM hr_expense_sheet s
         WHERE s._tmp = x.id
    """)

    util.remove_column(cr, 'hr_expense_sheet', '_tmp')
    todel = 'accounting_date department_id journal_id bank_journal_id account_move_id'.split()
    for f in todel:
        util.remove_field(cr, 'hr.expense', f)
