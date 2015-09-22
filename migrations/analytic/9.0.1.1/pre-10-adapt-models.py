# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        WITH tmplvw AS (
            SELECT id
              FROM account_analytic_account
             WHERE state='template'
                OR type='view'
        ),
        del_lines AS (
            DELETE FROM account_analytic_line
                  WHERE account_id IN (SELECT id FROM tmplvw)
        )
        DELETE FROM account_analytic_account
              WHERE id IN (SELECT id FROM tmplvw)
    """)

    models = util.splitlines("""
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
    """)

    # we need analytic journals in the sale_contract migration
    # we'll delete the model there if it's installed
    if not util.table_exists(cr, 'account_analytic_invoice_line'):
        models.append('account.analytic.journal')

    for model in models:
        util.delete_model(cr, model)
