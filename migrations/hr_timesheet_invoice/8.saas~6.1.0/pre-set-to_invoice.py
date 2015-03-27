# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("SELECT id FROM hr_timesheet_invoice_factor WHERE factor=100 LIMIT 1")
    [factor_id] = cr.fetchone() or [None]
    if not factor_id:
        # no factor found, create one
        cr.execute("""INSERT INTO hr_timesheet_invoice_factor(name, customer_name, factor)
                           VALUES ('0%', 'No Invoicing', 100.0)
                        RETURNING id
                   """)
        [factor_id] = cr.fetchone() or [None]

    # for the contract that was using timesheet, set a "free" factor
    cr.execute("""UPDATE account_analytic_account
                     SET to_invoice = %s
                   WHERE to_invoice IS NULL
                     AND use_timesheets = true
               """, [factor_id])
