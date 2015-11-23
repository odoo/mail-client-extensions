# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        During computation of fields.function that are stored, process is really slow due to 
        a problem with the workflow transition that computes a lot of time a field which he should
        not. So for the sake of this migration, we will deactivate the transition before computing
        the stored fields and reactivate it after.
    """
    cr.execute("""UPDATE wkf_transition SET condition='False and reconciled' WHERE condition = 'reconciled'""")
    cr.execute("""UPDATE wkf_transition SET condition='False and not reconciled' WHERE condition = 'not reconciled'""")
    
    # Compute matched_percentage on account_move
    cr.execute("""UPDATE account_move m 
                    SET matched_percentage = CASE WHEN t2.total_amount = 0 THEN 1.0 ELSE t2.total_reconciled/t2.total_amount END
                    FROM (SELECT aml.move_id, sum(round(abs(aml.balance),4)) AS total_amount, 
                                sum(round(abs(aml.balance),4)-round(abs(aml.amount_residual),4)) AS total_reconciled
                            FROM account_move_line aml, account_account a
                            WHERE a.id = aml.account_id AND a.internal_type IN ('receivable', 'payable') 
                            GROUP BY move_id) AS t2 
                    WHERE t2.move_id = m.id
            """)

    cr.execute("""UPDATE account_move m SET matched_percentage = 1 WHERE matched_percentage IS NULL""")

    # Compute debit_cash_basis, credit_cash_basis and balance_cash_basis on account_move_line

    cr.execute("""UPDATE account_move_line aml
                    SET debit_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.debit ELSE aml.debit*move.matched_percentage END,
                        credit_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.credit ELSE aml.credit*move.matched_percentage END,
                        balance_cash_basis = CASE WHEN j.type in ('sale', 'purchase') THEN aml.balance ELSE (aml.debit*move.matched_percentage) - (aml.credit*move.matched_percentage) END
                    FROM account_move move, account_journal j
                    WHERE aml.move_id = move.id AND aml.journal_id = j.id
            """)

    # Compute other fields via ORM

    env = util.env(cr)
    cr.execute("""SELECT id FROM account_move_line WHERE amount_residual IS NULL""")
    ids = [row[0] for row in cr.fetchall()]
    aml = env['account.move.line'].browse(ids)
    for name in ('amount_residual', 'amount_residual_currency', 'reconciled'):
        field = aml._fields[name]
        aml._recompute_todo(field)

    cr.execute("""SELECT inv.id FROM account_invoice inv, res_company c
                    WHERE c.id = inv.company_id and c.currency_id != inv.currency_id
                """)
    inv_ids = [row[0] for row in cr.fetchall()]
    invoices = env['account.invoice'].browse(inv_ids)
    for name in ('amount_total_company_signed', 'amount_total_signed', 'amount_untaxed_signed'):
        field = invoices._fields[name]
        invoices._recompute_todo(field)

    aml.recompute()

    # aml field will trigger the computation of residual field on invoice

    cr.execute("""UPDATE wkf_transition SET condition='reconciled' WHERE condition = 'False and reconciled'""")
    cr.execute("""UPDATE wkf_transition SET condition='not reconciled' WHERE condition = 'False and not reconciled'""")

    # Check that we don't have any invoices that have not been calculated by the orm
    # If we do, it is an error and it is possible that someone has create the invoice with an account not reconciliable and we should
    # warn the user that he should do smth about that
    cr.execute("""SELECT id FROM account_invoice WHERE state = 'open' and residual_signed IS NULL""")
    invoices = cr.fetchall()
    if len(invoices) != 0:
        cr.execute("""
            SELECT inv.id FROM account_invoice inv, account_account a
            WHERE inv.account_id = a.id AND a.reconcile = 'f'
        """)
        unrecs = cr.fetchall()
        if unrecs:
            msg_unrecs = (
                "\n{count_unrec} of them (ID:{unrec_ids}) have been set on "
                "unreconciliable accounts, which is wrong").format(
                    count_unrec=len(unrecs),
                    unrec_ids=[row[0] for row in unrecs])
        else:
            msg_unrecs = (
                "\nNo invoices were set on unreconciliable accounts. You need "
                "to search in another direction.")
        msg = (
            "{count_inv} invoices have not been correctly computed. please "
            "check them as it probably means a huge user mistake that needs "
            "attention. ID: {faulty_ids}{msg_unrecs}").format(
                count_inv=len(invoices),
                faulty_ids=[row[0] for row in invoices],
                msg_unrecs=msg_unrecs,
            )
        raise util.MigrationError(msg)
