# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    cr.execute(
        """
         SELECT id
           FROM account_analytic_account
          WHERE state='template'
             OR type='view'
        """
    )

    sz = 10000
    for aaa in util.chunks((a for a, in cr.fetchall()), sz, fmt=tuple):
        cr.execute("SELECT id FROM account_analytic_line WHERE account_id IN %s", [aaa])
        for aal in util.chunks((a for a, in cr.fetchall()), sz, fmt=tuple):
            util.remove_records(cr, "account.analytic.line", aal)

        util.remove_records(cr, "account.analytic.account", aaa)

    models = list(util.splitlines("""
        account.analytic.balance

        report.account.report_analyticbalance
        report.account.report_analyticcostledger
        report.account.report_invertedanalyticbalance
        report.account.report_analyticjournal
        report.account.report_analyticcostledgerquantity

        account.analytic.cost.ledger.journal.report
        account.analytic.cost.ledger
        account.analytic.inverted.balance
        account.analytic.journal.report
    """))

    # we need analytic journals in the sale_contract migration
    # we'll delete the model there if it's installed
    if not util.table_exists(cr, 'account_analytic_invoice_line'):
        models.append('account.analytic.journal')

    for model in models:
        util.delete_model(cr, model)

    #Reintroduced account_type cancelled in commit f6d6762dc7150076b5463b09480222db813b2cf1 so we need to migrate them
    util.create_column(cr, 'account_analytic_account', 'account_type', 'varchar')
    cr.execute("""UPDATE account_analytic_account
                    SET account_type = CASE WHEN state IN ('close', 'cancelled') THEN 'closed' ELSE 'normal' END
                """)
